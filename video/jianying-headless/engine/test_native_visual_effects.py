"""Resource-backed visual plans: bindings, controls, restrictions and isolation."""
import argparse
from copy import deepcopy
import json
from pathlib import Path
import unittest
from unittest.mock import patch

import jy14_headless as j
import native_export as export
import native_resources as resources
import native_visual_effects as visual


class VisualEffectTests(unittest.TestCase):
    def setUp(self):
        self.plan = j.read_json(FIXTURE / 'visual-effects-plan.json')
        self.record = j.read_json(FIXTURE / 'visual-effects-build-v1/build.json')
        h = j.nd.helper()
        self.timeline = h._decrypt_metadata_in_memory(FIXTURE / 'visual-effects-build-v1/draft/draft_info.json')
        self.metadata = h._decrypt_metadata_in_memory(FIXTURE / 'visual-effects-build-v1/draft/draft_meta_info.json')
        self.target = Path(self.record['target'])

    def verify(self):
        return j.verify_structure(self.timeline, self.metadata, self.plan, self.record['assets'], self.target)

    def test_full_build_has_three_owned_resources_one_media_and_native_controls(self):
        record = j.verify_build(FIXTURE / 'visual-effects-build-v1')
        self.assertEqual(len(record['native_resources']), 3)
        self.assertEqual(len(record['assets']), 1)
        self.assertEqual(record['duration_us'], 6000000)
        self.assertEqual(len(self.timeline['tracks']), 5)
        self.assertEqual([m['value'] for m in self.timeline['materials']['effects'] if m['type'] == 'filter'], [1, .45])
        params = self.timeline['materials']['video_effects'][0]['adjust_params']
        self.assertEqual([p['value'] for p in params], [.25, .5])
        for r in record['native_resources']:
            self.assertFalse(r['redistribution_authorized'])
            self.assertFalse(r['usage']['entitlement_verified'])

    def test_tracks_do_not_create_media_registrations_or_source_ranges(self):
        for track in self.timeline['tracks'][1:3]:
            for seg in track['segments']:
                self.assertNotIn('source_timerange', seg)
        registrations = j.read_json(FIXTURE / 'visual-effects-build-v1/draft/key_value.json')
        self.assertEqual(len(registrations), 1)

    def test_unknown_names_fields_or_download_urls_are_rejected(self):
        for index in (1, 2):
            plan = deepcopy(self.plan)
            plan['tracks'][index]['segments'][0]['name'] = 'online-unverified'
            with self.assertRaisesRegex(ValueError, 'no current native capture'):
                j.validate_plan(plan)
            plan = deepcopy(self.plan)
            plan['tracks'][index]['segments'][0]['url'] = 'https://example.invalid/resource'
            with self.assertRaisesRegex(ValueError, 'unsupported fields'):
                j.validate_plan(plan)

    def test_filter_strength_requires_finite_normalized_number(self):
        for value in (-.1, 1.01, True, float('nan'), float('inf'), '0.5'):
            with self.assertRaises(ValueError):
                visual.validate({'name': 'hd-monochrome', 'strength': value}, 'filter')

    def test_effect_controls_reject_unknown_and_nonfinite_values(self):
        for params in ({'frequency': .5}, {'range': False}, {'speed': float('nan')}, [], {'range': 1.01}):
            with self.assertRaises(ValueError):
                visual.validate({'name': 'light-shake', 'params': params}, 'effect')

    def test_duplicate_effect_track_and_outside_duration_fail(self):
        self.plan['tracks'].append(deepcopy(self.plan['tracks'][1]))
        with self.assertRaisesRegex(ValueError, 'Stacked tracks'):
            j.validate_plan(self.plan)
        self.plan['tracks'].pop()
        self.plan['tracks'][2]['segments'][0]['duration_us'] = 5000000
        with self.assertRaisesRegex(ValueError, 'fit within'):
            j.validate_plan(self.plan)

    def test_filter_strength_and_effect_parameter_changes_are_detected(self):
        node = next(m for m in self.timeline['materials']['effects'] if m['type'] == 'filter')
        node['value'] = .9
        with self.assertRaisesRegex(ValueError, 'strength changed'):
            self.verify()
        node['value'] = 1
        self.timeline['materials']['video_effects'][0]['adjust_params'][0]['value'] = .9
        with self.assertRaisesRegex(ValueError, 'parameter changed'):
            self.verify()

    def test_missing_effect_parameter_is_not_silently_defaulted(self):
        self.timeline['materials']['video_effects'][0]['adjust_params'].pop()
        with self.assertRaisesRegex(ValueError, 'parameters changed'):
            self.verify()

    def test_primary_resource_binding_cannot_be_changed_to_other_bucket(self):
        self.timeline['tracks'][1]['segments'][0]['material_id'] = self.timeline['materials']['video_effects'][0]['id']
        with self.assertRaisesRegex(ValueError, 'primary material binding changed'):
            self.verify()

    def test_flower_style_cannot_silently_ignore_requested_colors_or_wrong_track(self):
        spec = self.plan['tracks'][3]['segments'][0]
        for field in ('color', 'border_color', 'border_width'):
            with self.assertRaisesRegex(ValueError, 'owns fill and stroke'):
                visual.validate(dict(spec, **{field: '#FFFFFF' if field != 'border_width' else .05}), 'text')
        with self.assertRaisesRegex(ValueError, 'text segment'):
            visual.validate(spec, 'video')

    def test_missing_flower_binding_and_changed_style_path_are_detected(self):
        seg = self.timeline['tracks'][3]['segments'][0]
        refs = seg['extra_material_refs'][:]
        seg['extra_material_refs'] = []
        with self.assertRaisesRegex(ValueError, 'Text effect binding changed'):
            self.verify()
        seg['extra_material_refs'] = refs
        node = next(m for m in self.timeline['materials']['texts'] if m['id'] == seg['material_id'])
        content = json.loads(node['content'])
        content['styles'][0]['effectStyle']['path'] = '/unrelated/resource'
        node['content'] = json.dumps(content)
        with self.assertRaisesRegex(ValueError, 'path changed'):
            self.verify()

    def test_native_identical_flower_duplicate_is_accepted_but_conflict_is_not(self):
        node = next(m for m in self.timeline['materials']['effects'] if m['type'] == 'text_effect')
        duplicate = deepcopy(node)
        self.timeline['materials']['effects'].append(duplicate)
        self.timeline['tracks'][3]['segments'][0]['extra_material_refs'].append(node['id'])
        self.verify()
        duplicate['resource_id'] = 'different'
        with self.assertRaisesRegex(ValueError, 'Conflicting duplicate'):
            self.verify()

    def test_flower_base_style_cannot_gain_unplanned_color_or_strokes(self):
        seg = self.timeline['tracks'][3]['segments'][0]
        node = next(m for m in self.timeline['materials']['texts'] if m['id'] == seg['material_id'])
        content = json.loads(node['content'])
        content['styles'][0]['fill']['content']['solid']['color'] = [1, 0, 0]
        node['content'] = json.dumps(content)
        with self.assertRaisesRegex(ValueError, 'base fill or stroke changed'):
            self.verify()
        content['styles'][0]['fill']['content']['solid']['color'] = [1, 1, 1]
        content['styles'][0]['strokes'] = [{'width': .5}]
        node['content'] = json.dumps(content)
        with self.assertRaisesRegex(ValueError, 'base fill or stroke changed'):
            self.verify()

    def test_flower_uses_new_text_and_utf16_style_range(self):
        spec = dict(self.plan['tracks'][3]['segments'][0], text='花字😀')
        material = deepcopy(j.blueprint()['text']['materials'][0][1])
        j.text_material(material, spec)
        material['id'] = 'new-text'
        materials = {'texts': [material]}
        segment = {'material_id': material['id']}
        visual.apply_text(segment, materials, spec, self.target)
        content = json.loads(material['content'])
        self.assertEqual(content['text'], '花字😀')
        self.assertEqual(content['styles'][0]['range'], [0, 4])
        self.assertNotIn('strokes', content['styles'][0])
        self.assertEqual(len(materials['effects']), 1)

    def test_usage_restrictions_cannot_be_dropped_from_inventory(self):
        records = deepcopy(self.record['native_resources'])
        records[0].pop('usage')
        with self.assertRaisesRegex(ValueError, 'usage boundary changed'):
            resources.verify_files(records, FIXTURE / 'visual-effects-build-v1/draft', self.plan)

    def test_resource_cache_unchanged_and_missing_source_is_rejected(self):
        for record in self.record['native_resources']:
            entry = resources.definition(record['key'])
            actual = resources.tree_manifest(entry['source'])
            self.assertTrue(all(actual.get(name) == info for name, info in entry['files'].items()))
            resources.verify_cached_manifest(entry, actual, 'Cache changed')
        fake = resources.definition(self.record['native_resources'][0]['key'])
        fake['source'] = str(WORK / 'missing')
        with patch.object(resources, 'definition', return_value=fake):
            with self.assertRaises(FileNotFoundError):
                resources.prepare(self.plan, WORK / 'must-not-copy', {'runtime_profile': self.record['runtime_profile']})
        self.assertFalse((WORK / 'must-not-copy').exists())

    def test_only_exact_native_generated_cache_outputs_are_accepted(self):
        entry = resources.definition('filter/hd-monochrome')
        actual = dict(entry['files'], **entry['native_generated_cache_files'])
        self.assertEqual(len(resources.verify_cached_manifest(entry, actual, 'Cache changed')), 1)
        self.assertEqual(resources.verify_cached_manifest(entry, entry['files'], 'Cache changed'), [])
        added = next(iter(entry['native_generated_cache_files']))
        for bad in (dict(actual, **{added: {'sha256': '0' * 64, 'size': 32352}}),
                    dict(actual, **{'unrecognized.metallib': {'sha256': '0' * 64, 'size': 1}})):
            with self.assertRaisesRegex(ValueError, 'Cache changed'):
                resources.verify_cached_manifest(entry, bad, 'Cache changed')
        actual.pop(next(iter(entry['files'])))
        with self.assertRaisesRegex(ValueError, 'Cache changed'):
            resources.verify_cached_manifest(entry, actual, 'Cache changed')

    def test_new_build_copies_original_packages_without_gpu_cache_outputs(self):
        dest = WORK / 'fresh-resource-copy'
        records = resources.prepare(self.plan, dest, {'runtime_profile': self.record['runtime_profile']})
        for record in records:
            entry = resources.definition(record['key'])
            self.assertEqual(resources.tree_manifest(dest / record['relative']), entry['files'])
            for name in entry.get('native_generated_cache_files', {}):
                self.assertFalse((dest / record['relative'] / name).exists())
        self.assertEqual(sum(len(r.get('source_generated_cache_files_not_copied', [])) for r in records), 3)

    def test_known_export_preflight_and_unknown_effect_fails_before_creating_job(self):
        checked = export.supported_features(self.timeline)
        self.assertEqual({w['resource'] for w in checked['warnings']},
                         {'effect/light-shake', 'filter/hd-monochrome', 'text-effect/orange-outline'})
        bad = deepcopy(self.timeline)
        bad['materials']['effects'][0]['resource_id'] = 'not-captured'
        out = WORK / 'must-not-export'
        with patch.object(export, 'verified_build', return_value=(FIXTURE / 'visual-effects-build-v1', self.record, bad)), \
                self.assertRaisesRegex(ValueError, 'Unverified native filter/text effect identity'):
            export.run(FIXTURE / 'visual-effects-build-v1', out)
        self.assertFalse(out.exists())


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--fixture', type=Path, required=True)
    parser.add_argument('--work', type=Path, required=True)
    args = parser.parse_args()
    FIXTURE, WORK = args.fixture.resolve(), args.work.resolve()
    WORK.mkdir(parents=True, exist_ok=False)
    result = unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(VisualEffectTests))
    j.write(WORK / 'result.json', {'tests': result.testsRun, 'passed': result.wasSuccessful(),
                                 'live_written': False, 'cache_changed': False, 'export_attempted': False})
    raise SystemExit(not result.wasSuccessful())

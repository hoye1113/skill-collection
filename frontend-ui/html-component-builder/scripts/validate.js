#!/usr/bin/env node
'use strict';

const fs = require('fs');
const path = require('path');

// ========== Helpers ==========

function findComponentFiles(dir) {
  var files = [];

  var componentsDir = path.join(dir, 'components');
  if (fs.existsSync(componentsDir)) {
    var entries = fs.readdirSync(componentsDir);
    for (var i = 0; i < entries.length; i++) {
      var compFile = path.join(componentsDir, entries[i], 'component.html');
      if (fs.existsSync(compFile)) {
        files.push(compFile);
      }
    }
  }

  var pagesDir = path.join(dir, 'pages');
  if (fs.existsSync(pagesDir)) {
    var pageEntries = fs.readdirSync(pagesDir);
    for (var p = 0; p < pageEntries.length; p++) {
      var pageCompDir = path.join(pagesDir, pageEntries[p], 'components');
      if (fs.existsSync(pageCompDir)) {
        var comps = fs.readdirSync(pageCompDir);
        for (var c = 0; c < comps.length; c++) {
          var pcFile = path.join(pageCompDir, comps[c], 'component.html');
          if (fs.existsSync(pcFile)) {
            files.push(pcFile);
          }
        }
      }
    }
  }

  return files;
}

function getComponentName(filePath) {
  return path.basename(path.dirname(filePath));
}

function stripCSSComments(css) {
  return css.replace(/\/\*[\s\S]*?\*\//g, function(match) {
    return match.replace(/[^\n]/g, ' ');
  });
}

function extractTagContents(html, tag) {
  var results = [];
  var pattern = new RegExp('<' + tag + '([^>]*)>([\\s\\S]*?)<\\/' + tag + '>', 'gi');
  var match;
  while ((match = pattern.exec(html)) !== null) {
    results.push({
      attrs: match[1],
      content: match[2],
      startIndex: match.index,
      fullMatch: match[0]
    });
  }
  return results;
}

function getLineNumber(content, position) {
  return content.substring(0, position).split('\n').length;
}

function getComponentRelPath(filePath, projectDir) {
  return path.relative(projectDir, filePath).replace(/\\/g, '/');
}

function extractStyleBlocks(html) {
  var results = [];
  var pattern = /<style([^>]*)>([\s\S]*?)<\/style>/gi;
  var match;
  while ((match = pattern.exec(html)) !== null) {
    var beforeMatch = html.substring(0, match.index);
    var startLine = beforeMatch.split('\n').length;
    results.push({
      content: match[2],
      startLine: startLine
    });
  }
  return results;
}

function extractScriptBlocks(html) {
  var results = [];
  var pattern = /<script([^>]*)>([\s\S]*?)<\/script>/gi;
  var match;
  while ((match = pattern.exec(html)) !== null) {
    if (!/src\s*=/i.test(match[1])) {
      var beforeMatch = html.substring(0, match.index);
      var startLine = beforeMatch.split('\n').length;
      results.push({
        content: match[2],
        startLine: startLine
      });
    }
  }
  return results;
}

// ========== Check 1: CSS Namespacing ==========

function checkCSSNamespacing(files, projectDir) {
  var total = files.length;
  var passed = 0;
  var violations = [];

  for (var i = 0; i < files.length; i++) {
    var filePath = files[i];
    var name = getComponentName(filePath);
    var relPath = getComponentRelPath(filePath, projectDir);
    var filePassed = true;

    try {
      var html = fs.readFileSync(filePath, 'utf8');
      var styleBlocks = extractStyleBlocks(html);

      for (var s = 0; s < styleBlocks.length; s++) {
        var block = styleBlocks[s];
        var cleanedCSS = stripCSSComments(block.content);
        var rules = cleanedCSS.split('}');

        var blockContentOffset = html.indexOf(block.content);
        var linesBeforeBlock = blockContentOffset >= 0
          ? html.substring(0, blockContentOffset).split('\n').length - 1
          : block.startLine - 1;

        for (var r = 0; r < rules.length; r++) {
          var rule = rules[r].trim();
          if (!rule) continue;

          var braceIndex = rule.indexOf('{');
          if (braceIndex === -1) continue;

          var selectorPart = rule.substring(0, braceIndex).trim();
          if (!selectorPart) continue;
          if (selectorPart.charAt(0) === '@') continue;

          var selectors = selectorPart.split(',');
          for (var si = 0; si < selectors.length; si++) {
            var selector = selectors[si].trim();
            if (!selector) continue;

            var lower = selector.toLowerCase();
            if (lower.indexOf(':root') === 0) continue;
            if (lower.indexOf('html') === 0 && (lower.length === 4 || !/\w/.test(lower.charAt(4)))) continue;
            if (lower.indexOf('body') === 0 && (lower.length === 4 || !/\w/.test(lower.charAt(4)))) continue;
            if (selector.charAt(0) === '@') continue;

            var prefix = '.cmp-' + name;
            if (selector.indexOf('*') !== -1) continue;

            if (selector.indexOf(prefix) !== 0) {
              var ruleText = rules.slice(0, r + 1).join('}');
              var approxLine = linesBeforeBlock + ruleText.split('\n').length;

              violations.push({
                file: relPath,
                line: approxLine,
                message: 'Selector "' + selector + '" does not start with "' + prefix + '"'
              });
              filePassed = false;
            }
          }
        }
      }
    } catch (err) {
      violations.push({ file: relPath, line: 0, message: 'Error reading file: ' + err.message });
      filePassed = false;
    }

    if (filePassed) passed++;
  }

  return { total: total, passed: passed, violations: violations, label: 'CSS namespacing' };
}

// ========== Check 2: JS IIFE Wrapping ==========

function checkIIFEWrapping(files, projectDir) {
  var violations = [];

  for (var i = 0; i < files.length; i++) {
    var filePath = files[i];
    var relPath = getComponentRelPath(filePath, projectDir);

    try {
      var html = fs.readFileSync(filePath, 'utf8');
      var scripts = extractScriptBlocks(html);

      for (var s = 0; s < scripts.length; s++) {
        var script = scripts[s];
        var content = script.content;
        var trimmed = content.trim();

        if (!trimmed) continue;

        var hasIIFE = /\(function\s*\(\s*componentRoot\s*\)\s*\{/.test(trimmed);

        if (!hasIIFE) {
          var firstLines = trimmed.split('\n');
          var firstLine = '';
          for (var fl = 0; fl < firstLines.length; fl++) {
            firstLine = firstLines[fl].trim();
            if (firstLine && firstLine.charAt(0) !== '/' && firstLine.indexOf('*') !== 0) break;
          }
          var scriptLine = getLineNumber(html, html.indexOf(content));
          violations.push({
            file: relPath,
            line: scriptLine,
            message: 'Script not wrapped in IIFE. First line: ' + firstLine.substring(0, 60)
          });
          continue;
        }

        var lines = content.split('\n');
        for (var li = 0; li < lines.length; li++) {
          var line = lines[li].trim();

          if (/\}\s*\)\s*\(\s*document\.(querySelector|getElementById)\s*\(/.test(line)) continue;
          if (/(?:var|const|let)\s+\w+\s*=\s*document\.(querySelector|getElementById)\s*\(\s*['"]/.test(line)) continue;
          if (/document\.addEventListener/.test(line)) continue;
          if (/document\.dispatchEvent/.test(line)) continue;

          if (/document\.querySelector\s*\(/.test(line) || /document\.getElementById\s*\(/.test(line)) {
            violations.push({
              file: relPath,
              line: script.startLine + li,
              message: line.substring(0, 80) + ' (use componentRoot instead)'
            });
          }
        }
      }
    } catch (err) {
      violations.push({ file: relPath, line: 0, message: 'Error reading file: ' + err.message });
    }
  }

  return { violations: violations, label: 'JS IIFE wrapping' };
}

// ========== Check 3: data-component Attribute ==========

function checkDataComponentAttr(files, projectDir) {
  var total = files.length;
  var passed = 0;
  var violations = [];

  for (var i = 0; i < files.length; i++) {
    var filePath = files[i];
    var name = getComponentName(filePath);
    var relPath = getComponentRelPath(filePath, projectDir);

    try {
      var html = fs.readFileSync(filePath, 'utf8');
      var hasAttr = false;

      var attrPattern = new RegExp('data-component\\s*=\\s*["\']?' + name.replace(/[-/\\^$*+?.()|[\]{}]/g, '\\$&') + '["\']?', 'i');
      if (attrPattern.test(html)) {
        hasAttr = true;
      }

      if (!hasAttr) {
        violations.push({
          file: relPath,
          line: 0,
          message: 'Missing data-component="' + name + '" attribute in body element'
        });
      } else {
        passed++;
      }
    } catch (err) {
      violations.push({ file: relPath, line: 0, message: 'Error reading file: ' + err.message });
    }
  }

  return { total: total, passed: passed, violations: violations, label: 'data-component attribute' };
}

// ========== Check 4: components.json Conformance ==========

function checkComponentsJson(files, projectDir) {
  var violations = [];
  var configPath = path.join(projectDir, 'components.json');

  if (!fs.existsSync(configPath)) {
    return { violations: violations, label: 'components.json conformance', skipped: true, skipReason: 'components.json not found' };
  }

  var config;
  try {
    config = JSON.parse(fs.readFileSync(configPath, 'utf8'));
  } catch (err) {
    return { violations: [{ file: 'components.json', line: 0, message: 'Invalid JSON: ' + err.message }], label: 'components.json conformance', skipped: false };
  }

  var registeredComponents = {};
  var componentsList = [];
  
  // 支持两种格式：扁平格式 { components: [...] } 和页面格式 { pages: { pageName: { components: [...] } } }
  if (config.components && Array.isArray(config.components)) {
    componentsList = config.components;
  } else if (config.pages) {
    for (var pageName in config.pages) {
      var pageConfig = config.pages[pageName];
      if (pageConfig.components && Array.isArray(pageConfig.components)) {
        for (var ci = 0; ci < pageConfig.components.length; ci++) {
          var comp = pageConfig.components[ci];
          // 创建副本并添加 page 信息
          var compCopy = JSON.parse(JSON.stringify(comp));
          compCopy.page = pageName;
          componentsList.push(compCopy);
        }
      }
    }
  }

  for (var i = 0; i < componentsList.length; i++) {
    var comp = componentsList[i];
    var name = comp.name;
    var scope = comp.scope || 'shared';
    var page = comp.page || '';

    var expectedPath;
    if (scope === 'shared') {
      expectedPath = path.join(projectDir, 'components', name, 'component.html');
    } else if (scope === 'page') {
      expectedPath = path.join(projectDir, 'pages', page, 'components', name, 'component.html');
    } else {
      expectedPath = path.join(projectDir, 'components', name, 'component.html');
    }

    registeredComponents[name + '|' + scope + '|' + page] = expectedPath;

    if (!fs.existsSync(expectedPath)) {
      violations.push({
        file: 'components.json',
        line: 0,
        message: 'Missing component file: ' + name + ' (expected at ' + path.relative(projectDir, expectedPath).replace(/\\/g, '/') + ')'
      });
    }
  }

  for (var fi = 0; fi < files.length; fi++) {
    var filePath = files[fi];
    var compName = getComponentName(filePath);
    var normalizedRelPath = path.relative(projectDir, filePath).replace(/\\/g, '/');

    var found = false;
    for (var ri = 0; ri < componentsList.length; ri++) {
      var reg = componentsList[ri];
      var regScope = reg.scope || 'shared';
      var regPage = reg.page || '';

      var regPath;
      if (regScope === 'shared') {
        regPath = ('components/' + reg.name + '/component.html');
      } else if (regScope === 'page') {
        regPath = ('pages/' + regPage + '/components/' + reg.name + '/component.html');
      } else {
        regPath = ('components/' + reg.name + '/component.html');
      }

      if (regPath === normalizedRelPath) {
        found = true;
        break;
      }
    }

    if (!found) {
      violations.push({
        file: getComponentRelPath(filePath, projectDir),
        line: 0,
        message: 'Unregistered component (not in components.json): ' + compName
      });
    }
  }

  return { violations: violations, label: 'components.json conformance', skipped: false };
}

// ========== Check 5: Cross-component DOM Access ==========

function checkCrossComponentAccess(files, projectDir) {
  var violations = [];

  for (var i = 0; i < files.length; i++) {
    var filePath = files[i];
    var relPath = getComponentRelPath(filePath, projectDir);

    try {
      var html = fs.readFileSync(filePath, 'utf8');
      var scripts = extractScriptBlocks(html);

      for (var s = 0; s < scripts.length; s++) {
        var script = scripts[s];
        var content = script.content;

        var iifeMatch = content.match(/\(function\s*\(\s*componentRoot\s*\)\s*\{([\s\S]*?)\}\s*\)/);
        if (!iifeMatch) continue;

        var iifeBody = iifeMatch[1];
        var lines = iifeBody.split('\n');

        for (var li = 0; li < lines.length; li++) {
          var line = lines[li].trim();

          if (!line) continue;
          if (/document\.addEventListener/.test(line)) continue;
          if (/document\.dispatchEvent/.test(line)) continue;

          if (/document\.querySelector\s*\(/.test(line)) {
            violations.push({
              file: relPath,
              line: script.startLine + li,
              message: line.substring(0, 80) + ' (use componentRoot.querySelector instead)'
            });
          }
          if (/document\.getElementById\s*\(/.test(line)) {
            violations.push({
              file: relPath,
              line: script.startLine + li,
              message: line.substring(0, 80) + ' (use componentRoot.querySelector instead)'
            });
          }
          if (/document\.querySelectorAll\s*\(/.test(line)) {
            violations.push({
              file: relPath,
              line: script.startLine + li,
              message: line.substring(0, 80) + ' (use componentRoot.querySelectorAll instead)'
            });
          }
        }
      }
    } catch (err) {
      violations.push({ file: relPath, line: 0, message: 'Error reading file: ' + err.message });
    }
  }

  return { violations: violations, label: 'Cross-component DOM access' };
}

// ========== Main ==========

function main() {
  var args = process.argv.slice(2);
  var projectDir = process.cwd();

  for (var a = 0; a < args.length; a++) {
    if (args[a] === '--dir' && a + 1 < args.length) {
      projectDir = path.resolve(args[a + 1]);
      a++;
    }
  }

  if (!fs.existsSync(projectDir)) {
    console.error('Error: Directory not found: ' + projectDir);
    process.exit(1);
  }

  console.log('Validating project at: ' + projectDir);
  console.log('');

  var files = findComponentFiles(projectDir);

  if (files.length === 0) {
    var noComponents =
      !fs.existsSync(path.join(projectDir, 'components')) &&
      !fs.existsSync(path.join(projectDir, 'pages'));
    if (noComponents) {
      console.log('No components found. Expected components/ or pages/ directory.');
    } else {
      console.log('No components found.');
    }
    process.exit(1);
  }

  var r1 = checkCSSNamespacing(files, projectDir);
  var r2 = checkIIFEWrapping(files, projectDir);
  var r3 = checkDataComponentAttr(files, projectDir);
  var r4 = checkComponentsJson(files, projectDir);
  var r5 = checkCrossComponentAccess(files, projectDir);

  var totalIssues = 0;

  function printResult(result) {
    if (result.skipped) {
      console.log('[SKIP] ' + result.label + ': ' + result.skipReason);
      return;
    }

    var vCount = result.violations.length;
    totalIssues += vCount;

    if (vCount === 0) {
      if (result.total !== undefined) {
        console.log('[PASS] ' + result.label + ': ' + result.passed + '/' + result.total + ' components passed');
      } else {
        console.log('[PASS] ' + result.label + ': no violations');
      }
    } else {
      var issueWord = vCount === 1 ? 'issue' : 'issues';
      if (result.label === 'components.json conformance' && vCount > 0) {
        console.log('[FAIL] ' + result.label + ': ' + vCount + ' ' + issueWord);
      } else {
        console.log('[FAIL] ' + result.label + ': ' + vCount + ' ' + issueWord);
      }
      for (var vi = 0; vi < result.violations.length; vi++) {
        var v = result.violations[vi];
        var lineStr = v.line > 0 ? ':' + v.line : '';
        console.log('  - ' + v.file + lineStr + ' \u2014 ' + v.message);
      }
    }
  }

  printResult(r1);
  printResult(r2);
  printResult(r3);
  printResult(r4);
  printResult(r5);

  console.log('');

  if (totalIssues === 0) {
    console.log('Summary: All checks passed. ' + files.length + ' components validated.');
    process.exit(0);
  } else {
    var issueWord = totalIssues === 1 ? 'issue' : 'issues';
    console.log('Summary: ' + totalIssues + ' ' + issueWord + ' found across ' + files.length + ' components.');
    process.exit(1);
  }
}

main();

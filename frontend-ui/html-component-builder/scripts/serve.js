#!/usr/bin/env node

'use strict';

var http = require('http');
var fs = require('fs');
var path = require('path');
var url = require('url');

// ─── MIME type map ──────────────────────────────────────────────────────────

var MIME_TYPES = {
  '.html': 'text/html; charset=utf-8',
  '.css': 'text/css; charset=utf-8',
  '.js': 'application/javascript; charset=utf-8',
  '.json': 'application/json; charset=utf-8',
  '.png': 'image/png',
  '.jpg': 'image/jpeg',
  '.jpeg': 'image/jpeg',
  '.gif': 'image/gif',
  '.svg': 'image/svg+xml',
  '.webp': 'image/webp',
  '.woff': 'font/woff',
  '.woff2': 'font/woff2'
};

var DEFAULT_MIME = 'application/octet-stream';

// ─── SSE reload script ──────────────────────────────────────────────────────

var SSE_SCRIPT =
  '<script>(function(){\n' +
  '  var es = new EventSource(\'/__sse\');\n' +
  '  es.addEventListener(\'message\', function(e){ if(e.data===\'reload\') location.reload(); });\n' +
  '})();</script>';

// ─── CLI argument parsing ───────────────────────────────────────────────────

function parseArgs(argv) {
  var args = argv.slice(2);
  var opts = {
    dir: process.cwd(),
    port: 3000,
    reload: false,
    open: true
  };

  for (var i = 0; i < args.length; i++) {
    switch (args[i]) {
      case '--dir':
        opts.dir = path.resolve(args[++i] || '.');
        break;
      case '--port':
        opts.port = parseInt(args[++i], 10) || 3000;
        break;
      case '--reload':
        opts.reload = true;
        break;
      case '--no-open':
        opts.open = false;
        break;
    }
  }

  return opts;
}

// ─── MIME lookup ────────────────────────────────────────────────────────────

function getMime(filePath) {
  return MIME_TYPES[path.extname(filePath).toLowerCase()] || DEFAULT_MIME;
}

// ─── Component discovery ────────────────────────────────────────────────────

function discoverComponents(baseDir) {
  var shared = [];
  var pageGroups = {};

  // Shared: components/*/component.html
  var sharedDir = path.join(baseDir, 'components');
  if (fs.existsSync(sharedDir)) {
    try {
      var entries = fs.readdirSync(sharedDir, { withFileTypes: true });
      for (var i = 0; i < entries.length; i++) {
        var entry = entries[i];
        if (entry.isDirectory()) {
          var compFile = path.join(sharedDir, entry.name, 'component.html');
          if (fs.existsSync(compFile)) {
            shared.push(path.join('components', entry.name, 'component.html').replace(/\\/g, '/'));
          }
        }
      }
    } catch (_e) { /* ignore */ }
  }

  // Page-specific: pages/*/components/*/component.html
  var pagesDir = path.join(baseDir, 'pages');
  if (fs.existsSync(pagesDir)) {
    try {
      var pages = fs.readdirSync(pagesDir, { withFileTypes: true });
      for (var p = 0; p < pages.length; p++) {
        var page = pages[p];
        if (!page.isDirectory()) continue;

        var pageCompDir = path.join(pagesDir, page.name, 'components');
        if (!fs.existsSync(pageCompDir)) continue;

        try {
          var pageEntries = fs.readdirSync(pageCompDir, { withFileTypes: true });
          var found = [];
          for (var j = 0; j < pageEntries.length; j++) {
            var pe = pageEntries[j];
            if (pe.isDirectory()) {
              var peFile = path.join(pageCompDir, pe.name, 'component.html');
              if (fs.existsSync(peFile)) {
                found.push(
                  path.join('pages', page.name, 'components', pe.name, 'component.html').replace(/\\/g, '/')
                );
              }
            }
          }
          if (found.length > 0) {
            pageGroups[page.name] = found;
          }
        } catch (_e) { /* ignore */ }
      }
    } catch (_e) { /* ignore */ }
  }

  return { shared: shared, pages: pageGroups };
}

function printComponents(components) {
  var hasShared = components.shared.length > 0;
  var pageNames = Object.keys(components.pages);
  var hasPages = pageNames.length > 0;

  if (!hasShared && !hasPages) return;

  console.log('Discovering components...');

  if (hasShared) {
    console.log('  Shared components/');
    for (var i = 0; i < components.shared.length; i++) {
      console.log('    - ' + components.shared[i]);
    }
  }

  for (var p = 0; p < pageNames.length; p++) {
    var pageName = pageNames[p];
    var files = components.pages[pageName];
    console.log('  Page pages/' + pageName + '/components/');
    for (var f = 0; f < files.length; f++) {
      console.log('    - ' + files[f]);
    }
  }
}

// ─── Get local IP ───────────────────────────────────────────────────────────

function getLocalIP() {
  var os = require('os');
  var interfaces = os.networkInterfaces();
  var names = Object.keys(interfaces);
  for (var i = 0; i < names.length; i++) {
    var addrs = interfaces[names[i]];
    for (var j = 0; j < addrs.length; j++) {
      var addr = addrs[j];
      if (addr.family === 'IPv4' && !addr.internal) {
        return addr.address;
      }
    }
  }
  return '127.0.0.1';
}

// ─── Open browser (cross-platform) ──────────────────────────────────────────

function openBrowser(urlStr) {
  var cp = require('child_process');
  var platform = process.platform;
  var cmd, cmdArgs;

  if (platform === 'win32') {
    cmd = 'cmd';
    cmdArgs = ['/c', 'start', '', urlStr];
  } else if (platform === 'darwin') {
    cmd = 'open';
    cmdArgs = [urlStr];
  } else {
    cmd = 'xdg-open';
    cmdArgs = [urlStr];
  }

  try {
    cp.spawn(cmd, cmdArgs, { detached: true, stdio: 'ignore' }).unref();
  } catch (_e) { /* silently ignore */ }
}

// ─── SSE client management ──────────────────────────────────────────────────

var sseClients = [];

function notifyClients() {
  var msg = 'data: reload\n\n';
  for (var i = sseClients.length - 1; i >= 0; i--) {
    try {
      sseClients[i].write(msg);
    } catch (_e) {
      sseClients.splice(i, 1);
    }
  }
}

// ─── File watcher ───────────────────────────────────────────────────────────

function startWatcher(watchDir) {
  try {
    fs.watch(watchDir, { recursive: true }, function (_eventType, filename) {
      if (!filename) return;
      var ext = path.extname(filename).toLowerCase();
      if (ext === '.html' || ext === '.css' || ext === '.js') {
        notifyClients();
      }
    });
  } catch (_e) {
    console.log('Warning: Could not start file watcher.');
  }
}

// ─── Inject reload script into HTML ────────────────────────────────────────

function injectReloadScript(html) {
  var bodyCloseIdx = html.indexOf('</body>');
  if (bodyCloseIdx !== -1) {
    return html.slice(0, bodyCloseIdx) + SSE_SCRIPT + html.slice(bodyCloseIdx);
  }
  return html + SSE_SCRIPT;
}

// ─── Request handler ────────────────────────────────────────────────────────

function createRequestHandler(baseDir, enableReload) {
  return function (req, res) {
    var parsedUrl = url.parse(req.url, true);
    var pathname = decodeURIComponent(parsedUrl.pathname);

    // CORS headers on all responses
    res.setHeader('Access-Control-Allow-Origin', '*');
    res.setHeader('Access-Control-Allow-Methods', 'GET, OPTIONS');
    res.setHeader('Access-Control-Allow-Headers', '*');

    // Handle CORS preflight
    if (req.method === 'OPTIONS') {
      res.writeHead(204);
      res.end();
      return;
    }

    // SSE endpoint
    if (pathname === '/__sse') {
      res.writeHead(200, {
        'Content-Type': 'text/event-stream',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive'
      });
      res.write('data: connected\n\n');
      sseClients.push(res);

      req.on('close', function () {
        var idx = sseClients.indexOf(res);
        if (idx !== -1) {
          sseClients.splice(idx, 1);
        }
      });
      return;
    }

    // Resolve file path
    var safePath = path.normalize(pathname).replace(/^(\.\.[\/\\])+/, '');
    var filePath = path.join(baseDir, safePath);

    // Security: ensure resolved path is within baseDir
    if (path.resolve(filePath).indexOf(path.resolve(baseDir)) !== 0) {
      res.writeHead(403, { 'Content-Type': 'text/plain; charset=utf-8' });
      res.end('403 - Forbidden');
      return;
    }

    // Check if path exists
    var stat = null;
    try {
      stat = fs.statSync(filePath);
    } catch (_e) {
      var relPath = path.relative(baseDir, filePath);
      res.writeHead(404, { 'Content-Type': 'text/plain; charset=utf-8' });
      res.end('404 - File not found: ' + relPath);
      return;
    }

    // Directory → serve index.html
    if (stat.isDirectory()) {
      filePath = path.join(filePath, 'index.html');
      try {
        stat = fs.statSync(filePath);
      } catch (_e) {
        var relPath2 = path.relative(baseDir, filePath);
        res.writeHead(404, { 'Content-Type': 'text/plain; charset=utf-8' });
        res.end('404 - File not found: ' + relPath2);
        return;
      }
    }

    // Read and serve file
    var ext = path.extname(filePath).toLowerCase();
    var contentType = getMime(filePath);

    try {
      if (enableReload && (ext === '.html' || ext === '.htm')) {
        var content = fs.readFileSync(filePath, 'utf-8');
        content = injectReloadScript(content);
        res.writeHead(200, { 'Content-Type': contentType });
        res.end(content);
      } else {
        var data = fs.readFileSync(filePath);
        res.writeHead(200, { 'Content-Type': contentType });
        res.end(data);
      }
    } catch (_readErr) {
      res.writeHead(500, { 'Content-Type': 'text/plain; charset=utf-8' });
      res.end('500 - Internal Server Error');
    }
  };
}

// ─── Main ───────────────────────────────────────────────────────────────────

function main() {
  var config = parseArgs(process.argv);

  // Validate directory
  if (!fs.existsSync(config.dir)) {
    console.error('Error: Directory not found: ' + config.dir);
    process.exit(1);
  }

  // Scan and print components
  var components = discoverComponents(config.dir);
  printComponents(components);

  // Create server
  var handler = createRequestHandler(config.dir, config.reload);
  var server = http.createServer(handler);

  // Start file watcher if --reload
  if (config.reload) {
    startWatcher(config.dir);
    console.log('Live reload: enabled');
  }

  // Handle errors
  server.on('error', function (err) {
    if (err.code === 'EADDRINUSE') {
      console.error('Error: Port ' + config.port + ' is already in use. Try: node serve.js --port ' + (config.port + 1));
      process.exit(1);
    } else {
      console.error('Error: ' + err.message);
      process.exit(1);
    }
  });

  // Start listening
  server.listen(config.port, function () {
    var localIP = getLocalIP();
    console.log('');
    console.log('Server running at:');
    console.log('  Local:   http://localhost:' + config.port + '/');
    console.log('  Network: http://' + localIP + ':' + config.port + '/');
    console.log('');

    // Auto-open browser
    if (config.open) {
      openBrowser('http://localhost:' + config.port + '/');
    }
  });
}

main();

const http = require('http');
const fs = require('fs');
const path = require('path');

const server = http.createServer((req, res) => {
    const basePath = req.url === '/' ? './index.html' : `.${req.url}`;
    const filePath = basePath.startsWith('/node_modules')
        ? `.${req.url}`
        : basePath;

    const extname = path.extname(filePath);
    const contentType = {
        '.html': 'text/html',
        '.css': 'text/css',
        '.js': 'application/javascript',
    }[extname] || 'application/octet-stream';

    fs.readFile(filePath, (err, data) => {
        if (err) {
            if (err.code === 'ENOENT') {
                res.writeHead(404, {'Content-Type': 'text/plain'});
                res.end('404 Not Found');
            } else {
                res.writeHead(500, {'Content-Type': 'text/plain'});
                res.end('Internal Server Error');
            }
        } else {
            res.writeHead(200, {'Content-Type': contentType});
            res.end(data);
        }
    });
});

server.listen(3000, () => {
    console.log('Server running at http://localhost:3000/');
});

const http = require('http');
const fs = require('fs');
const app = require('express');

// Path based arugments are passed manually so you will have to switch them out for your own path
// there are 2 of them so search for ./Javascript/Node Server/form-data.json

const server = http.createServer((req, res) => {
  if (req.method === 'GET') {
    res.writeHead(200, { 'Content-Type': 'text/html' });
    res.write(
                `
                <html>
                  <head>
                    <style>
                      body {
                        font-family: sans-serif;
                        width: 500px;
                        margin: 0 auto;
                      }
                      
                      label {
                        display: block;
                        margin-bottom: 5px;
                      }
                      
                      input[type="text"] {
                        width: 100%;
                        height: 32px;
                        padding: 0 8px;
                        font-size: 16px;
                        border: 1px solid #ccc;
                        border-radius: 4px;
                        box-sizing: border-box;
                      }
                      
                      input[type="submit"] {
                        width: 100%;
                        height: 32px;
                        margin-top: 20px;
                        background-color: #4caf50;
                        color: white;
                        border: none;
                        border-radius: 4px;
                        font-size: 16px;
                        cursor: pointer;
                      }
                      
                      span {
                        color: red;
                        font-size: 14px;
                        display: block;
                        margin-top: 5px;
                      }
                    </style>
                  </head>
                  <body>
                    <form action="/submit" method="post">
                      <label for="firstName">First Name:</label>
                      <input type="text" id="firstName" name="firstName"><br>
                      <label for="lastName">Last Name:</label>
                      <input type="text" id="lastName" name="lastName"><br>
                      <label for="email">Email:</label>
                      <input type="text" id="email" name="email"><br>
                      <input type="submit" value="Submit">
                    </form>
                  </body>
                </html>
                `
    );
    return res.end();
  } else if (req.method === 'POST') {
    let body = '';
    req.on('data', chunk => {
      body += chunk.toString(); // convert Buffer to string
    });
    req.on('end', () => {
      const formData = body.split('&').map(pair => pair.split('='));
      const data = formData.reduce((acc, pair) => {
        acc[pair[0]] = decodeURIComponent(pair[1]);
        return acc;
      }, {});
      const emailRegex = /^[a-zA-Z0-9.!#$%&'*+/=?^_`{|}~-]+@[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(?:\.[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*$/;        
        if (!emailRegex.test(data.email)) {
        res.writeHead(200, { 'Content-Type': 'text/html' });
        res.write(
              `
                  <html>
                    <head>
                      <style>
                        body {
                          font-family: sans-serif;
                          width: 500px;
                          margin: 0 auto;
                        }
                        
                        label {
                          display: block;
                          margin-bottom: 5px;
                        }
                        
                        input[type="text"] {
                          width: 100%;
                          height: 32px;
                          padding: 0 8px;
                          font-size: 16px;
                          border: 1px solid #ccc;
                          border-radius: 4px;
                          box-sizing: border-box;
                        }
                        
                        input[type="submit"] {
                          width: 100%;
                          height: 32px;
                          margin-top: 20px;
                          background-color: #4caf50;
                          color: white;
                          border: none;
                          border-radius: 4px;
                          font-size: 16px;
                          cursor: pointer;
                        }
                        
                        span {
                          color: red;
                          font-size: 14px;
                          display: block;
                          margin-top: 5px;
                        }
                      </style>
                    </head>
                    <body>
                      <form action="/submit" method="post">
                        <label for="firstName">First Name:</label>
                        <input type="text" id="firstName" name="firstName">
                        <label for="lastName">Last Name:</label>
                        <input type="text" id="lastName" name="lastName">
                        <label for="email">Email:</label>
                        <input type="text" id="email" name="email">
                        <span style="color: red">Error: Invalid email</span>
                        <input type="submit" value="Submit">
                      </form>
                    </body>
                  </html>
             `
        );
        return res.end();
      }
      // Generate unique ID and date for form submission
      const id = Date.now();
      const date = new Date().toLocaleString();

      // Append form submission to file
      fs.readFile('./Javascript/Node Server/form-data.json', 'utf8', (err, file) => {
        if (err) {
          console.error(err);
          res.writeHead(500, { 'Content-Type': 'text/html' });
          res.write('<html><body><h1>Error: 500 Internal Server Error</h1></body></html>');
          return res.end();
        }
        let submissions;
        if (file) {
          submissions = JSON.parse(file);
        } else {
          submissions = {};
        }
        submissions[id] = {
          firstName: data.firstName,
          lastName: data.lastName,
          email: data.email,
          date,
        };
        fs.writeFile('./Javascript/Node Server/form-data.json', JSON.stringify(submissions, null, 2), err => {
          if (err) {
            console.error(err);
            res.writeHead(500, { 'Content-Type': 'text/html' });
            res.write('<html><body><h1>Error: 500 Internal Server Error</h1></body></html>');
            return res.end();
              }
              res.writeHead(303, { 'Location': '/' });
              return res.end();
            });
          });
        });
      }
    });

server.listen(3000, () => {
  console.log('Listening on port 3000');
  console.log('http://localhost:3000')
});



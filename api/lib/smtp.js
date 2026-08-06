// Minimal SMTP client using Node.js built-ins (no external dependencies)
// Works perfectly in Vercel serverless

const tls = require('tls');

async function sendEmail({ host, port, secure, auth, from, to, subject, html }) {
  return new Promise((resolve, reject) => {
    const socket = tls.connect({
      host,
      port,
      servername: host,
    });

    let response = '';
    let step = 0;

    socket.on('data', (data) => {
      response += data.toString();
      const lines = response.split('\r\n');
      
      // Process complete SMTP responses (end with code + space)
      const lastLine = lines[lines.length - 2]; // -1 is empty, -2 is last line
      if (!lastLine || !lastLine.match(/^\d{3} /)) return;
      
      response = ''; // Reset for next command
      const code = parseInt(lastLine.substring(0, 3));

      try {
        switch(step) {
          case 0: // Initial connection
            if (code !== 220) throw new Error(`SMTP connection failed: ${lastLine}`);
            socket.write(`EHLO ${host}\r\n`);
            step++;
            break;
            
          case 1: // EHLO response
            if (code !== 250) throw new Error(`EHLO failed: ${lastLine}`);
            socket.write('AUTH LOGIN\r\n');
            step++;
            break;
            
          case 2: // AUTH LOGIN
            if (code !== 334) throw new Error(`AUTH LOGIN failed: ${lastLine}`);
            socket.write(Buffer.from(auth.user).toString('base64') + '\r\n');
            step++;
            break;
            
          case 3: // Username sent
            if (code !== 334) throw new Error(`AUTH username failed: ${lastLine}`);
            socket.write(Buffer.from(auth.pass).toString('base64') + '\r\n');
            step++;
            break;
            
          case 4: // Password sent
            if (code !== 235) throw new Error(`AUTH password failed: ${lastLine}`);
            socket.write(`MAIL FROM:<${auth.user}>\r\n`);
            step++;
            break;
            
          case 5: // MAIL FROM
            if (code !== 250) throw new Error(`MAIL FROM failed: ${lastLine}`);
            socket.write(`RCPT TO:<${to}>\r\n`);
            step++;
            break;
            
          case 6: // RCPT TO
            if (code !== 250) throw new Error(`RCPT TO failed: ${lastLine}`);
            socket.write('DATA\r\n');
            step++;
            break;
            
          case 7: // DATA command
            if (code !== 354) throw new Error(`DATA failed: ${lastLine}`);
            
            // Build email message
            const message = [
              `From: ${from}`,
              `To: ${to}`,
              `Subject: ${subject}`,
              'MIME-Version: 1.0',
              'Content-Type: text/html; charset=UTF-8',
              '',
              html,
              '.',
              ''
            ].join('\r\n');
            
            socket.write(message);
            step++;
            break;
            
          case 8: // Message sent
            if (code !== 250) throw new Error(`Message send failed: ${lastLine}`);
            socket.write('QUIT\r\n');
            step++;
            break;
            
          case 9: // QUIT
            socket.end();
            resolve({ success: true, messageId: lastLine });
            break;
        }
      } catch (error) {
        socket.destroy();
        reject(error);
      }
    });

    socket.on('error', (error) => {
      reject(new Error(`SMTP socket error: ${error.message}`));
    });

    socket.on('timeout', () => {
      socket.destroy();
      reject(new Error('SMTP connection timeout'));
    });

    socket.setTimeout(30000); // 30 second timeout
  });
}

module.exports = { sendEmail };

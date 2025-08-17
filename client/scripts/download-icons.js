import fs from 'fs';
import https from 'https';
import path from 'path';

const icons = [
  { url: 'https://lightning-s3.s3.amazonaws.com/static/website/img/apple-touch-icon.png', filename: 'apple-touch-icon.png' },
  { url: 'https://lightning-s3.s3.amazonaws.com/static/website/img/favicon-32x32.png', filename: 'favicon-32x32.png' },
  { url: 'https://lightning-s3.s3.amazonaws.com/static/website/img/favicon-16x16.png', filename: 'favicon-16x16.png' },
  { url: 'https://lightning-s3.s3.amazonaws.com/static/website/img/favicon.ico', filename: 'favicon.ico' }
];

const downloadDir = './scripts/icons';
if (!fs.existsSync(downloadDir)) fs.mkdirSync(downloadDir, { recursive: true });

for (const icon of icons) {
  const filePath = path.join(downloadDir, icon.filename);
  const file = fs.createWriteStream(filePath);
  https.get(icon.url, (response) => {
    response.pipe(file);
    console.log(`✅ Downloaded ${icon.filename}`);
  });
}

// scripts/cache-bust.js

const fs = require('fs');
const path = require('path');

const indexPath = path.join(__dirname, '../client/dist/index.html');

fs.readFile(indexPath, 'utf8', (err, data) => {
  if (err) {
    console.error('❌ Failed to read index.html:', err);
    process.exit(1);
  }

  const timestamp = Date.now();
  const busted = data.replace(/(src="[^"]+\.js)(\?v=\d+)?"/g, `$1?v=${timestamp}"`);

  fs.writeFile(indexPath, busted, 'utf8', (err) => {
    if (err) {
      console.error('❌ Failed to write cache-busted index.html:', err);
      process.exit(1);
    }

    console.log(`✅ Cache-busted index.html with ?v=${timestamp}`);
  });
});

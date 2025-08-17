export function cacheBusterPlugin() {
  return {
    name: 'vite-plugin-cachebuster',
    enforce: 'post',
    generateBundle(_, bundle) {
      const timestamp = Date.now();
      for (const fileName of Object.keys(bundle)) {
        if (fileName.endsWith('.js')) {
          const chunk = bundle[fileName];
          if (chunk.code) {
            chunk.code = chunk.code.replace(
              /(<script.+src=["'].*?)(["'])/g,
              `$1?v=${timestamp}$2`
            );
          }
        }
      }
    },
  };
}

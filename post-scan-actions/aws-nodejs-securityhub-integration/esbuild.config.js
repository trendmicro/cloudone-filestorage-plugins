const { nodeExternalsPlugin } = require('esbuild-node-externals')
const rimraf = require('rimraf')
const fs = require('fs')
const archiver = require('archiver')

const OUT_DIR = 'dist'

async function main() {
  rimraf.sync(OUT_DIR)
  rimraf.sync('bundle.zip')

  await require('esbuild')
    .build({
      entryPoints: ['lambda/index.js'],
      outfile: 'dist/index.js',
      bundle: true,
      minify: false,
      sourcemap: true,
      format: 'cjs',
      platform: 'node',
      keepNames: true,
      plugins: [
        nodeExternalsPlugin({
          // This will include dependencies in the bundle
          dependencies: false
        })
      ],
      // Exclude aws sdk v3 as node18.x runtime has aws sdk v3 already
      external: ['@aws-sdk/*'],
      treeShaking: true,
      metafile: true
    })
    .catch((err) => {
      console.error(err)
      process.exit(1)
    })

  await zipDirectory(`${OUT_DIR}/`, 'bundle.zip')
}

function zipDirectory(source, outputTarget) {
  const archive = archiver('zip', { zlib: { level: 9 }, store: true });
  const stream = fs.createWriteStream(outputTarget, { flags: 'w' })

  stream.on("close", () => {
    console.log(archive.pointer() + ' total bytes');
    console.log('archiver has been finalized and the output file descriptor has closed.')
  });

  return new Promise(async (resolve, reject) => {
    archive.pipe(stream)
    archive.on("error", err => reject(err))
    archive.directory(source, false)
    await archive.finalize()
    resolve()
  })
}

console.time('Built in')

main()
  .then(() => {
    console.timeEnd('Built in')
  })
  .catch((err) => {
    console.error(err)
    throw err
  })

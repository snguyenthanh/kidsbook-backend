/*
    instruction of usage:

    write your page index javascript file as [appname]/static/xxx.js
    but include in the page as /static/bundle/[appname]/xxx.js
    we suggest you name your index javascript file (i.e. xxx.js) as [pagename]_index.js
*/

const path = require('path')
const glob = require('glob')
const lessToJs = require('less-vars-to-js')
const fs = require('fs')
// const BundleAnalyzerPlugin = require('webpack-bundle-analyzer').BundleAnalyzerPlugin
const webpack = require('webpack')
// const CompressionPlugin = require('compression-webpack-plugin')

// const themeVariables = lessToJs(fs.readFileSync(path.join(__dirname, './ant-theme-vars.less'), 'utf8'))

/**
 * search for all .js file under [appname]/static/
 * for each, add the following key-value pair to the entries object:
 *    [appname]/[filename].js: [path to this .js file]
 * @returns the entries object as explained above
 */
function getEntries() {
  const filePaths = glob.sync('./kidsbook/*/static/*.js')
  var entries = {}
  for (var filePath of filePaths) {
    var splits = filePath.split('/')
    var appName = splits[splits.length - 3]
    var fileName = splits[splits.length - 1].split('.')[0]
    entries[appName + '/' + fileName] = filePath
  }
  return entries
}

module.exports = {
  entry: getEntries,
  output: {
    path: path.resolve('./kidsbook/bundled_static/prod/bundle'),
    filename: '[name].js'
  },
  plugins: [
    // new BundleAnalyzerPlugin(),
    new webpack.IgnorePlugin(/^\.\/locale$/, /moment$/),
    // new CompressionPlugin()
  ],
  resolve: {
    // please refer to the following links for explanation:
    // https://moduscreate.com/es6-es2015-import-no-relative-path-webpack/
    // https://webpack.js.org/configuration/resolve/#resolve-modules
    modules: [
      'node_modules',
      path.resolve(__dirname, 'kidsbook/comm_assets'),
    ],
    alias: {
      vue: 'vue/dist/vue.js',
      CommAssets: path.resolve(__dirname, 'kidsbook/comm_assets'),
    },
  },
  module: {
    rules: [
      // use babel-loader with es2015 and react settign to load .js and .jsx files
      {
        test: /.jsx?$/,
        loader: 'babel-loader',
        exclude: /node_modules/,
        query: {
          presets: ['babel-preset-env', 'react', 'stage-2'],
          plugins: [
            'transform-regenerator', [
              'import', [{
                'libraryName': 'antd',
                'style': true,
              }]
            ]
          ]
        }
      }, {
        test: /\.css$/,
        loader: 'style-loader!css-loader'
      }, {
        test: /\.less$/,
        use: [
          {loader: 'style-loader'},
          {loader: 'css-loader'},
          {loader: 'less-loader',
            options: {
              // modifyVars: themeVariables
            }
          }
        ]
      }, {
        test: /\.vue$/,
        loader: 'vue-loader'
      }, {
        test: /\.(eot|svg|ttf|woff|woff2)(\?\S*)?$/,
        loader: 'file-loader',
        options: {
          publicPath: '/static/bundle/'
        }
      },
    ],
  },
}





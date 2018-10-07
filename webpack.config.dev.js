const path = require('path')
const webpack = require('webpack')


/***** import webpack.config.js as the base configuration *****/
const prodConfig = require('./webpack.config.js')
var devConfig = prodConfig


/**************** modify the following settings: **************/

// change the destination path of the bundled javascript files
// from ./kidsbook/bundled_static/prod/bundle
// to   ./kidsbook/bundled_static/dev/bundle
devConfig.output.path = path.resolve('./kidsbook/bundled_static/dev/bundle')

// set the mode to watch
// so whenever the files get changed, the bundle will be updated accordingly immediately
devConfig.watch = true
devConfig.watchOptions = {
  ignored: /node_modules/,
  poll: 800  // every 1.8 seconds, webpack checks file update
}

devConfig.plugins = [
  new webpack.IgnorePlugin(/^\.\/locale$/, /moment$/),
]

module.exports = devConfig

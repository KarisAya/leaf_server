const path = require("path");
const HTMLWebpackPlugin = require("html-webpack-plugin");

lessUse = [
    "style-loader",
    "css-loader",
    {
        loader: "postcss-loader",
        options: {postcssOptions: {plugins: [["postcss-preset-env",{ browsers: "last 2 versions" }]]}}
    },
    "less-loader"
]
module.exports = {
    mode:"production",
    entry:"./src/index.ts",
    resolve:{extensions: ['.ts', '.js'],},   
    output:{path:path.resolve(__dirname,"../../main/src/server"), filename:"bundle.js",},
    module:{rules :[
        {test:/\.ts$/, use:"ts-loader", exclude:/node_modules/,},
        {test:/\.less$/, use:lessUse, exclude:/node_modules/,},
    ]},
    plugins:[
        new HTMLWebpackPlugin({template:"./src/index.html"}),
    ]
}
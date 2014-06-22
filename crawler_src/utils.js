var fs = require('fs');
var	cheerio = require('cheerio');
var async = require('async');

var utils = {
  removeHash : function (url){
    return url.replace(/#.*$/, '');
  },

  extractLinks : function(url, body, cb){
    var root = url.match(/^https?:\/\/[^\/]+/)[0] + '/';

    $ = cheerio.load(body);
    async.map($('a[href]').toArray(), function(item, cb){
      var href = $(item).attr('href');
      if (href.match(/^javascript/)) return cb();

      var url = utils.removeHash(href);
      if (!url.match(/^http/)){
        url = root + url.replace(/^\//, '');
      }

      cb(null, url);
    }, cb);
  },

  parseList : function (data) {
    data = data.toString().split('\n');
    data = data.filter(function(url){
      return url.length > 0;
    });
    return data;
  },

  loadListFile : function (path, cb) {
    fs.readFile(path, function(err, data){
      if(err) return cb(err);

      data = utils.parseList(data);
      cb(null, data);
    });
  },

  appendListFile : function (path, string, cb) {
    fs.appendFileSync(path, string + '\n');
    cb();
  }
};

module.exports = utils;

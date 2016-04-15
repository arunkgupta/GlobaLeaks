var fs = require('fs');
var specs = JSON.parse(fs.readFileSync('tests/end2end/specs.json'));

// The test directory for downloaded files
var tmpDir = '/tmp/';

exports.config = {
  framework: 'jasmine',

  baseUrl: 'http://127.0.0.1:8082/',

  troubleshoot: true,
  directConnect: true,

  params: {
    'testFileDownload': true,
    'tmpDir': tmpDir
  },

  specs: specs,

  capabilities: {
    'browserName': 'chrome',
    'chromeOptions': {
      prefs: {
        'download': {
          'prompt_for_download': false,
          'default_directory': tmpDir
        }
      }
    }
  },

  jasmineNodeOpts: {
    isVerbose: true,
    includeStackTrace: true,
    defaultTimeoutInterval: 60000
  }
};

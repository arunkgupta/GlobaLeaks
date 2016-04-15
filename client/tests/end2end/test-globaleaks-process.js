var utils = require('./utils.js');

var path = require('path');

var fileToUpload = path.resolve(__filename);

describe('globaLeaks process', function() {
  var tip_text = 'topsecret';
  var receipts = [];
  var comment = 'comment';
  var comment_reply = 'comment reply';
  var message = 'message';
  var message_reply = 'message reply';
  var receiver_username = "Recipient 1";
  var receiver_password = "ACollectionOfDiplomaticHistorySince_1966_ToThe_Pr esentDay#";

  var login_whistleblower = function(receipt) {
    return protractor.promise.controlFlow().execute(function() {
      var deferred = protractor.promise.defer();

      browser.get('/#/');

      element(by.model('formatted_keycode')).sendKeys(receipt).then(function() {
        element(by.css('[data-ng-click="view_tip(formatted_keycode)"]')).click().then(function() {
          utils.waitForUrl('/status');
          deferred.fulfill();
        });
      });

      return deferred.promise;
    });
  };

  var login_receiver = function(username, password) {
    return protractor.promise.controlFlow().execute(function() {
      var deferred = protractor.promise.defer();

      browser.get('/#/login');

      element(by.model('loginUsername')).element(by.xpath(".//*[text()='" + username + "']")).click().then(function() {
        element(by.model('loginPassword')).sendKeys(password).then(function() {
          element(by.xpath('//button[contains(., "Log in")]')).click().then(function() {
            utils.waitForUrl('/receiver/tips');
            deferred.fulfill();
          });
        });
      });

      return deferred.promise;
    });
  };

  var perform_submission = function(done) {
    browser.get('/#/submission');

    browser.wait(function(){
      // Wait until the proof of work is resolved;
      return element(by.id('submissionForm')).evaluate('submission').then(function(submission) {
        return submission.pow === true;
      });
    });

    element(by.id('step-receiver-selection')).element(by.id('receiver-0')).click().then(function () {
      element(by.id('step-receiver-selection')).element(by.id('receiver-1')).click().then(function () {
        element(by.id('NextStepButton')).click().then(function () {
          element(by.id('step-0')).element(by.id('step-0-field-0-0-input-0')).sendKeys(tip_text).then(function () {
            if (utils.testFileUpload()) {
              browser.executeScript('angular.element(document.querySelector(\'input[type="file"]\')).attr("style", "opacity:0; visibility: visible;");');
              element(by.id('step-0')).element(by.id('step-0-field-2-0')).element(by.xpath("//input[@type='file']")).sendKeys(fileToUpload).then(function() {
                browser.waitForAngular();
                element(by.id('step-0')).element(by.id('step-0-field-2-0')).element(by.xpath("//input[@type='file']")).sendKeys(fileToUpload).then(function() {
                  browser.waitForAngular();
                  var submit_button = element(by.id('SubmitButton'));
                  var isClickable = protractor.ExpectedConditions.elementToBeClickable(submit_button);
                  browser.wait(isClickable);
                  submit_button.click().then(function() {
                    utils.waitForUrl('/receipt');
                    element(by.id('KeyCode')).getText().then(function (txt) {
                      receipts.unshift(txt);
                      element(by.id('ReceiptButton')).click().then(function() {
                        utils.waitForUrl('/status');
                        element(by.id('LogoutLink')).click().then(function() {
                          utils.waitForUrl('/');
                          done();
                        });
                      });
                    });
                  });
                });
              });
            } else {
              var submit_button = element(by.id('SubmitButton'));
              var isClickable = protractor.ExpectedConditions.elementToBeClickable(submit_button);
              browser.wait(isClickable);
              submit_button.click().then(function() {
                utils.waitForUrl('/receipt');
                element(by.id('KeyCode')).getText().then(function (txt) {
                  receipts.unshift(txt);
                  element(by.id('ReceiptButton')).click().then(function() {
                    utils.waitForUrl('/status');
                    element(by.id('LogoutLink')).click().then(function() {
                      utils.waitForUrl('/');
                      done();
                    });
                  });
                });
              });
            }
          });
        });
      });
    });
  };

  it('should redirect to /submission by clicking on the blow the whistle button', function(done) {
    browser.get('/#/');
    element(by.css('[data-ng-click="goToSubmission()"]')).click().then(function () {
      utils.waitForUrl('/submission');
      done();
    });
  });

  it('Whistleblowers should be able to submit tips (1)', function(done) {
    perform_submission(done);
  });

  it('Whistleblowers should be able to submit tips (2)', function(done) {
    perform_submission(done);
  });

  it('Whistleblowers should be able to submit tips (3)', function(done) {
    perform_submission(done);
  });

  it('Whistleblower should be able to access the first submission', function(done) {
    login_whistleblower(receipts[0]);
    expect(element(by.xpath("//*[contains(text(),'" + tip_text + "')]")).getText()).toEqual(tip_text);
    element(by.id('LogoutLink')).click().then(function() {
      utils.waitForUrl('/');
      done();
    });
  });

  it('Recipient should be able to access the first submission', function(done) {
    login_receiver(receiver_username, receiver_password);
    element(by.id('tip-0')).click().then(function() {
      expect(element(by.xpath("//*[contains(text(),'" + tip_text + "')]")).getText()).toEqual(tip_text);
      done();
    });
  });

  it('Recipient should be able to refresh tip page', function(done) {
    element(by.id('link-reload')).click().then(function () {
      browser.waitForAngular();
      done();
    });
  });

  it('Recipient should be able to see files and download them', function(done) {
    if (utils.testFileUpload()) {
      expect(element.all(by.cssContainingText("button", "download")).count()).toEqual(2);
      if (utils.testFileDownload()) {
        element.all(by.cssContainingText("button", "download")).get(0).click().then(function() {
          browser.waitForAngular();
          done();
        });
      } else {
        done();
      }
    } else {
      done();
    }
  });

  it('Recipient should be able to leave a comment to the whistleblower', function(done) {
    login_receiver(receiver_username, receiver_password);

    element(by.id('tip-0')).click().then(function() {
      element(by.model('tip.newCommentContent')).sendKeys(comment);
      element(by.id('comment-action-send')).click().then(function() {
        browser.waitForAngular();
        element(by.id('comment-0')).element(by.css('.preformatted')).getText().then(function(c) {
          expect(c).toContain(comment);
          element(by.id('LogoutLink')).click().then(function() {
            utils.waitForUrl('/login');
            done();
          });
        });
      });
    });
  });

  it('Whistleblower should be able to read the comment from the receiver and reply', function(done) {
    login_whistleblower(receipts[0]);

    element(by.id('comment-0')).element(by.css('.preformatted')).getText().then(function(c) {
      expect(c).toEqual(comment);
      element(by.model('tip.newCommentContent')).sendKeys(comment_reply);
      element(by.id('comment-action-send')).click().then(function() {
        browser.waitForAngular();
        element(by.id('comment-0')).element(by.css('.preformatted')).getText().then(function(c) {
          expect(c).toContain(comment_reply);
          done();
        });
      });
    });
  });

  it('Whistleblower should be able to attach a new file to the first submission', function(done) {
    if (utils.testFileUpload()) {
      login_whistleblower(receipts[0]);

      browser.executeScript('angular.element(document.querySelector(\'input[type="file"]\')).attr("style", "opacity:0; visibility: visible;");');
      element(by.xpath("//input[@type='file']")).sendKeys(fileToUpload).then(function() {
        browser.waitForAngular();
        element(by.xpath("//input[@type='file']")).sendKeys(fileToUpload).then(function() {
          browser.waitForAngular();
          // TODO: test file addition
          element(by.id('LogoutLink')).click().then(function() {
            utils.waitForUrl('/');
            done();
          });
        });
      });
    } else {
      done();
    }
  });

  it('Recipient should be able to start a private discussion with the whistleblower', function(done) {
    login_receiver(receiver_username, receiver_password);

    element(by.id('tip-0')).click().then(function() {
      element(by.model('tip.newMessageContent')).sendKeys(message);
      element(by.id('message-action-send')).click().then(function() {
        browser.waitForAngular();
        element(by.id('message-0')).element(by.css('.preformatted')).getText().then(function(m) {
          expect(m).toContain(message);
          element(by.id('LogoutLink')).click().then(function() {
            utils.waitForUrl('/login');
            done();
          });
        });
      });
    });
  });

  it('Whistleblower should be able to read the private message from the receiver and reply', function(done) {
    login_whistleblower(receipts[0]);

    element.all(by.options("obj.key as obj.value for obj in tip.msg_receivers_selector | orderBy:'value'")).get(1).click().then(function() {
      element(by.id('message-0')).element(by.css('.preformatted')).getText().then(function(message1) {
        expect(message1).toEqual(message);
        element(by.model('tip.newMessageContent')).sendKeys(message_reply);
        element(by.id('message-action-send')).click().then(function() {
          browser.waitForAngular();
          element(by.id('message-0')).element(by.css('.preformatted')).getText().then(function(message2) {
            expect(message2).toContain(message_reply);
            done();
          });
        });
      });
    });
  });

  it('Recipient should be able to export the submission', function(done) {
      login_receiver(receiver_username, receiver_password);
      element(by.id('tip-0')).click();
      element(by.id('tipFileName')).getText().then(function(t) {
        expect(t).toEqual(jasmine.any(String));
        element(by.id('tip-action-export')).click();
        if (utils.testFileDownload()) {
          // TODO: Verify the zips content
          utils.waitForFile(t + '.zip', 30000);
          done();
        } else {
          done();
        }
      });
  });

  it('Recipient should be able to disable and renable email notifications', function(done) {
    login_receiver(receiver_username, receiver_password);

    element(by.id('tip-0')).click();
    var silence = element(by.id('tip-action-silence'));
    silence.click();
    var notif = element(by.id('tip-action-notify'));
    notif.evaluate('tip.enable_notifications').then(function(enabled) {
      expect(enabled).toEqual(false);
      notif.click();
      silence.evaluate('tip.enable_notifications').then(function(enabled) {
        expect(enabled).toEqual(true);
        // TODO Determine if emails are actually blocked.
        done();
      });
    });
  });

  it('Recipient should be able to export first submission from the tips page', function(done) {
    if (utils.testFileDownload()) {
      login_receiver(receiver_username, receiver_password);

      var first_tip_export = element(by.id('tip-0')).element(by.id('tip-action-export'));
      first_tip_export.click();
      // TODO tests if the file has been downloaded and is valid
      done();
    } else {
      done();
    }
  });

  it('Recipient should be able to postpone all tips', function(done) {
    login_receiver(receiver_username, receiver_password);

    function make_dates(strings) {
      return strings.map(function(s) {
        expect(s).toEqual(jasmine.any(String));
        return new Date(s); 
      });
    }
      
    // Get the expiration dates of all of the tips.
    element.all(by.css('#tipListTableBody tr'))
        .evaluate('tip.expiration_date').then(function(exprs) {
      var start_expirations = make_dates(exprs); 
      // Postpone the expiration of all tips
      element(by.id('tip-action-select-all')).click();
      element(by.id('tip-action-postpone-selected')).click();
      element(by.id('modal-action-ok')).click();
      // Collect the new later expiration dates.
      element.all(by.css('#tipListTableBody tr'))
          .evaluate('tip.expiration_date').then(function(exprs) {
        var final_expirations = make_dates(exprs);
        
        // Zip start and final together, then reduce the combined array to a bool
        var b = final_expirations.map(function(e, i) {
          return [start_expirations[i], e];
        }).reduce(function(pv, cv) {
          var tmp = cv[0] < cv[1];
          return pv && tmp;
        }, true);

        // We expect that every final expiration is larger than its corresponding
        // initial value.
        expect(b).toEqual(true);
        done();
      });
    });
  });

  it('Recipient should be able to postpone first submission from its tip page', function(done) {
    login_receiver(receiver_username, receiver_password);
    
    element(by.id('tip-0')).click();
    // Get the tip's original expiration date.
    element(by.id('tipFileName')).evaluate('tip.expiration_date').then(function(d) {
      expect(d).toEqual(jasmine.any(String));
      var startExpiration = new Date(d);
      element(by.id('tip-action-postpone')).click();
      element(by.id('modal-action-ok')).click();

      element(by.id('tipFileName')).evaluate('tip.expiration_date').then(function(d) {
        expect(d).toEqual(jasmine.any(String));
        var newExpiration = new Date(d);
        expect(newExpiration).toBeGreaterThan(startExpiration);
        done();
      });
    });
  });

  it('Recipient should be able to delete first submission from its tip page', function(done) {
    login_receiver(receiver_username, receiver_password);

    // Find the uuid of the first tip.
    element(by.id('tip-0')).click();
    element(by.id('tipFileName')).evaluate('tip.id').then(function(tip_uuid) {
      element(by.id('tip-action-delete')).click();
      element(by.id('modal-action-ok')).click();
      
      // Ensure that the tip has disappeared from the recipient's view.
      element.all(by.css('#tipListTableBody tr')).evaluate('tip.id').then(function(uuids) {
        var i = uuids.indexOf(tip_uuid);
        expect(i).toEqual(-1);
        element(by.id('LogoutLink')).click().then(function() {
          utils.waitForUrl('/login');
          done();
        });
      });
    });
  });
});

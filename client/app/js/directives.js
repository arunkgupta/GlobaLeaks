angular.module('GLDirectives', []).
  directive('fadeout', function() {
    /* eslint-disable no-unused-vars */
    return function(scope, element, attrs) {
    /* eslint-enable no-unused-vars */
      var fadeout_delay = 3000;

      element.mouseenter(function() {
        element.stop().animate({opacity:'100'});
      });

      element.mouseleave(function() {
        element.fadeOut(fadeout_delay);
      });

      element.fadeOut(fadeout_delay);
    };
}).
  directive('inputPrefix', function() {
    return {
      require: 'ngModel',
      link: function(scope, elem, attrs, ngModel) {
        function inputPrefix(value) {
          var prefix = attrs.prefix;

          var result = prefix;

          if (value.length >= prefix.length) {
            if (value.slice(0, prefix.length) !== prefix) {
              result = prefix + value;
            } else {
              result = value;
            }
          }

          ngModel.$setViewValue(result);
          ngModel.$render();

          return result;
        }

        ngModel.$formatters.push(inputPrefix);
        ngModel.$parsers.push(inputPrefix);
      }
    };
}).
  directive('keycodevalidator', function() {
    return {
      require: 'ngModel',
      link: function(scope, elem, attrs, ngModel) {
        ngModel.$setValidity('keycodevalidator', false);
        ngModel.$parsers.unshift(function(viewValue) {
          var result = '';
          ngModel.$setValidity('keycodevalidator', false);
          viewValue = viewValue.replace(/\D/g,'');
          while (viewValue.length > 0) {
            result += viewValue.substring(0, 4);
            if(viewValue.length >= 4) {
              if (result.length < 19) {
                result += ' ';
              }
              viewValue = viewValue.substring(4);
            } else {
              break;
            }
          }
          angular.element(elem).val(result);
          if (result.length === 19) {
            ngModel.$setValidity('keycodevalidator', true);
          }
          return result;
        });
      }
    };
}).
 directive("fileread", function () {
   return {
     scope: {
       fileread: "="
     },
     /* eslint-disable no-unused-vars */
     link: function (scope, element, attributes) {
     /* eslint-enable no-unused-vars */
       element.bind('click', function(){
         element.val('');
       });

       element.bind("change", function (changeEvent) {
         var reader = new FileReader();
         reader.onload = function (e) {
           scope.$apply(function () {
             scope.fileread(e.target.result);
           });
         };
         reader.readAsText(changeEvent.target.files[0]);
       });
     }
   };
}).
directive('zxPasswordMeter', function() {
  return {
    scope: {
      value: "="
    },
    templateUrl: "views/partials/password_meter.html",
    link: function(scope) {
      scope.type = null;
      scope.text = '';

      scope.$watch('value', function(newValue) {
        if (newValue === undefined) {
          return;
        }

        if (newValue.password === 'undefined') { // <- intentionally as string
          // Short term fix for:
          // https://github.com/ghostbar/angular-zxcvbn/issues/13
          newValue.password = '';
        }

        if (newValue.password === '') {
          scope.type = null;
          scope.text = '';
        } else if (newValue.score < 3) {
          newValue.score = 1;
          scope.type = 'danger';
          scope.text = 'Weak';
        } else if (newValue.score < 4) {
          // guesses needed >= 10^8, <= 10^10
          scope.type = 'warning';
          scope.text = 'Acceptable';
        } else {
          // guesses needed >= 10^10
          scope.type = 'success';
          scope.text = 'Strong';
        }
      });
    }
  };
}).
directive('imageUpload', function () {
  return {
    restrict: 'A',
    scope: {
      imageUploadModel: '=',
      imageUploadModelAttr: '@',
      imageUploadUrl: '@'
    },
    templateUrl: 'views/partials/image_upload.html',
    controller: 'ImageUploadCtrl'
  };
}).
directive('uibDatepickerPopupa', function () {
  return {
    restrict: 'EAC',
    require: 'ngModel',
    link: function(scope, elem, attrs, ngModel) {
      ngModel.$parsers.push(function toModel(date) {
        return date.getFullYear() + '-' + (date.getMonth() + 1) + '-' + date.getDate();
      });
    }
  }
});

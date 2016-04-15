# -*- encoding: utf-8 -*-
#
# In here we shall keep track of all variables and objects that should be
# instantiated only once and be common to pieces of GLBackend code.

import operator

__author__ = u'Random GlobaLeaks Developers'
__copyright__ = u'2011-2016 - Hermes Center for Transparency and Digital Human Rights - GlobaLeaks Project'
__email__ = u'info@globaleaks.org'
__version__ = u'2.61.3'
__license__ = u'AGPL-3.0'

DATABASE_VERSION = 31
FIRST_DATABASE_VERSION_SUPPORTED = 15

# Add here by hand the languages supported!
# copy paste format from 'grunt updateTranslations'
LANGUAGES_SUPPORTED = [
 { "code": "ar", "name": "Arabic" },
 { "code": "bs", "name": "Bosnian" },
 { "code": "de", "name": "German" },
 { "code": "el", "name": "Greek" },
 { "code": "en", "name": "English" },
 { "code": "es", "name": "Spanish" },
 { "code": "fa", "name": "Persian" },
 { "code": "fr", "name": "French" },
 { "code": "he", "name": "Hebrew" },
 { "code": "hr_HR", "name": "Croatian (Croatia)" },
 { "code": "hu_HU", "name": "Hungarian (Hungary)" },
 { "code": "it", "name": "Italian" },
 { "code": "ja", "name": "Japanese" },
 { "code": "ka", "name": "Georgian" },
 { "code": "ko", "name": "Korean" },
 { "code": "nb_NO", "name": "Norwegian Bokmål (Norway)" },
 { "code": "nl", "name": "Dutch" },
 { "code": "pt_BR", "name": "Portuguese (Brazil)" },
 { "code": "pt_PT", "name": "Portuguese (Portugal)" },
 { "code": "ro", "name": "Romanian" },
 { "code": "ru", "name": "Russian" },
 { "code": "sq", "name": "Albanian" },
 { "code": "sv", "name": "Swedish" },
 { "code": "ta", "name": "Tamil" },
 { "code": "th", "name": "Thai" },
 { "code": "tr", "name": "Turkish" },
 { "code": "uk", "name": "Ukrainian" },
 { "code": "ur", "name": "Urdu" },
 { "code": "vi", "name": "Vietnamese" },
 { "code": "zh_CN", "name": "Chinese (China)" },
 { "code": "zh_TW", "name": "Chinese (Taiwan)" }
]

# Sorting the list of dict using the key 'code'
LANGUAGES_SUPPORTED.sort(key=operator.itemgetter('code'))

# Creating LANGUAGES_SUPPORTED_CODES form the ordered LANGUAGES_SUPPORTED
LANGUAGES_SUPPORTED_CODES = [i['code'] for i in LANGUAGES_SUPPORTED]

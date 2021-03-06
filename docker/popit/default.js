var path = require('path');

module.exports = {

    // by default use the compressed assets - this will apply to the test suite 
    // too
    public_dir: 'public-production',
    docs_dir:   path.normalize(__dirname + '/../docs'),

    show_dev_site_warning: false,

    server: {
      port: 8000,
    },

    force_https: false,

    logging: {
      log_level:      'info',
      colorize: false,
    },

    image_proxy: {
        path:       '/image-proxy/',
    },

    hosting_server: {
      // *.127.0.0.1.xip.io points to 127.0.0.1
        host:       'popit.parlamentoabierto.org.py',
        base_url:   'http://popit.parlamentoabierto.org.py:8000',
        email_from: 'PopIt <popit@parlamentoabierto.org.py>',
    },
    instance_server: {
        // This is used to create the url to the instance site. '%s' is
        // replaced with the instance name.
        base_url_format: "http://%s.popit.parlamentoabierto.org.py:8000",
        cookie_secret: 'hue2flu3rdle123',
        cookie_domain: 'parlamentoabierto.org.py',
        files_dir:     path.normalize(__dirname + '/../../popit_files'),
    },
    MongoDB: {
        host:         'localhost',
        port:         27017,
        master_name:  '_master',
        session_name: '_session',
        popit_prefix: 'popit_',        
    },
    email: {
        transport:         'Sendmail',
        transport_options: { },
        send_by_transport: true,
        save_to_database:  false,
        print_to_console:  false,
        bcc_to_sender:     true,
    },
    
    // default settings used if a site has not overidden them
    default_settings: {

        // used if instance owners do not set an email address
        email_from: 'DO NOT REPLY <popit@mysociety.org>',

        language: 'en',

        // Text taken from http://opendatacommons.org/licenses/odbl/
        license: [
          'The **{{name}}** PopIt instance is made available under the',
          '[Open Database License](http://opendatacommons.org/licenses/odbl/1.0/).',
          'Any rights in individual contents of the database are licensed under the',
          '[Database Contents License](http://opendatacommons.org/licenses/dbcl/1.0/).',
        ].join(' '),
    },

    queue: {
      prefix: 'popit_default_',
    },

    offline: false,
};

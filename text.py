def html(content, title='Oneself'):
    return """
    <!DOCTYPE HTML>
    <html>
        <style>
            @charset "utf-8";
            /* CSS Document */
            /*公共样式*/
            body {
                margin:0px;
                padding:0px;
                font-size: 12px;
                font-family: Arial, Helvetica, sans-serif;
            }
            ul, li, h1, h2, h3, h4, h5, h6, form, input {
                margin:0px;
                padding:0px
            }
            ul, li {
                list-style:none;
            }
            img {
                border:0px
            }
            a {
                text-decoration:none;
            }
            .fl {
                float: left;
            }
            .fr {
                float: right;
                position: relative;
            }
            .cf {
                clear: both;
            }
            .jh {
                color:#999;
            }
            #yc {
                color:#FFF;
            }
            .main {
                width: 1000px;
                margin-right: auto;
                margin-left: auto;
            }
        </style>
    
        <title>
            %s
        </title>
        <body>
            %s
        </body>
    </html>
    """ % (title, content)

#!/usr/bin/python

import BeautifulSoup    # << download this

import httplib, mimetypes
import re
import urllib2

HOST = 'speech.cs.cmu.edu'
PORT = '80'

def post_multipart(host, selector, fields, files):
    """
    Post fields and files to an http host as multipart/form-data.
    fields is a sequence of (name, value) elements for regular form fields.
    files is a sequence of (name, filename, value) elements for data to be uploaded as files
    Return the server's response page.
    """
    content_type, body = encode_multipart_formdata(fields, files)
    h = httplib.HTTP(host)
    h.putrequest('POST', selector)
    h.putheader('content-type', content_type)
    h.putheader('content-length', str(len(body)))
    h.endheaders()
    h.send(body)
    errcode, errmsg, headers = h.getreply()
    return h.file.read()

def encode_multipart_formdata(fields, files):
    """
    fields is a sequence of (name, value) elements for regular form fields.
    files is a sequence of (name, filename, value) elements for data to be uploaded as files
    Return (content_type, body) ready for httplib.HTTP instance
    """
    BOUNDARY = '---------------------------18710690068420275431780121534'
    CRLF = '\r\n'
    L = []
    for (key, value) in fields:
        L.append('--' + BOUNDARY)
        L.append('Content-Disposition: form-data; name="%s"' % key)
        L.append('')
        L.append(value)
    for (key, filename, value) in files:
        L.append('--' + BOUNDARY)
        L.append('Content-Disposition: form-data; name="%s"; filename="%s"' % (key, filename))
        L.append('Content-Type: %s' % get_content_type(filename))
        L.append('')
        L.append(value)
    L.append('--' + BOUNDARY + '--')
    L.append('')
    body = CRLF.join(L)
    content_type = 'multipart/form-data; boundary=%s' % BOUNDARY
    return content_type, body


def get_content_type(filename):
    return mimetypes.guess_type(filename)[0] or 'application/octet-stream'


def upload_corpus(corpusfile):
    content = open(corpusfile, 'r').read()
    file2upload = ("corpus", "corpusfile.txt", content)
    fields = ("formtype", "simple")
    files2upload = [file2upload]
    result = post_multipart("%s:%s" % (HOST, PORT),
                            "/cgi-bin/tools/lmtool.2.pl",
                            [fields],
                            files2upload)
    return result


def parse_dictionary_url(upload_result):
    """
    Given html such as:
    ...
    <a href="/tools/product//1172960283_24918/3290.dic">Dictionary</a>
    ..
    parse out the relative link and construct an absolute
    url and return to caller, eg:
    fife.speech.cs.cmu.edu/tools/product//1172960283_24918/3290.dic
    """

    # sanitize by removing stuff like this:
    # <!-- BASENAME >
    # find <!- followed by any character EXCEPT a '<' or a '>', and
    # keep search until finding a >
    matcher = re.compile('<!-([^<^>]*)>', re.I)
    upload_result = matcher.sub('',upload_result)

    # parse into data struct
    soup = BeautifulSoup.BeautifulSoup(upload_result)

    # find all links
    diclink = ""
    lmlink = ""
    links = soup('a')
    for link in links:
        linkstr = str(link)
        if linkstr.find(".dic") != -1:
            # found link of interest
            href = link['href']
            dicklink = "http://%s%s" % (HOST, href)
	
        if linkstr.find(".lm") != -1:
            # found link of interest
            href = link['href']
            lmlink =  "http://%s%s" % (HOST, href)
    return dicklink,lmlink


def dl_content(longurl, file2write):
    """ fetch the content from a url, write to given file """
    req = urllib2.Request(longurl)
    fd = urllib2.urlopen(req)
    sinkfd = open(file2write, 'w')
    while 1:
        data = fd.read(1024)
        sinkfd.write(data)
        if not len(data):
            break

def main(corpusfile):
    upload_result = upload_corpus(corpusfile)
    dictionary_url,lm_url = parse_dictionary_url(upload_result)
    dl_content(dictionary_url, corpusfile+".dic")
    dl_content(lm_url, corpusfile+".lm")



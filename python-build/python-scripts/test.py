from __future__ import print_function, unicode_literals
import sys
import types
import traceback

# Test imports.
import android
import time

droid = android.Android()
skip_gui = False


# tests for python modification for android {{{1
def test_029_isfile():                          # issue #29 {{{1
    import os
    # FIXME: determine path to sdcard. like: path = os.environ[""]
    path = "/sdcard"
    fname = os.path.join(path, "sl4a", "test_isfile")
    file(fname, "w").write("this is test")
    os.path.isfile(fname)
    os.remove(fname)
    try:
        assert os.path.isfile(fname) is False
    except Exception as e:
        print(e)
        return False
    return True


def test_047_ttyname():                         # issue #47 {{{1
    import os
    try:
        os.ttyname(0)
        os.ttyname(1)
    except Exception as e:
        print(e)
        return False
    return True


def test_071_anydbm():                          # issue #71 {{{1
    import os
    import anydbm
    # FIXME: determine path to sdcard. like: path = os.environ[""]
    del os.chmod
    for fname in (
        # failed: this is not SL4A application folder...
        # os.path.join("/data/data/com.googlecode.pythonforandroid",
        #              "files", "test_anydbm.dbm"),
        # OK: _chmod work well.
        # os.path.join("/data/local/abc", "test_anydbm.dbm"),
        # failed: _chmod not worked in FAT (SD card)
        os.path.join("/sdcard", "sl4a", "test_anydbm.dbm"),
    ):
        try:
            os.remove(fname + ".dat")
        except:
            pass
        anydbm.open(fname, "n")
        os.remove(fname + ".dat")
    return True


def test_075_httpserver():                      # issue #75 {{{1
    import time
    import threading
    import BaseHTTPServer
    fname = "/sdcard/sl4a/test_075.html"
    port = 9090

    class Handler(BaseHTTPServer.BaseHTTPRequestHandler):
        def do_GET(s):
            file(fname, "w").write("""
                <html><head></head><body>fine 075</body></html>""")
            html = open(fname, 'rb')
            s.send_response(200)
            s.send_header("Content-Type", "text/html")
            s.end_headers()
            s.wfile.write(html.read())

    server_class = BaseHTTPServer.HTTPServer
    httpd = server_class(('', port), Handler)
    if not skip_gui:
        # and manual test has passed, open http://127.0.0.1:9090 in browser.
        th = threading.Thread(target=httpd.serve_forever)
        th.start()
        droid.startActivity('android.intent.action.VIEW',
                            'http://127.0.0.1:9090/')
        time.sleep(3)
        httpd.shutdown()
    return True


def test_013s_scanBarcode():                # issue sl4a #13 {{{1
    if not skip_gui:
        code = droid.scanBarcode()
        ext = code.result.get('extras', None)
        if ext is None:
            return False
        if 'SCAN_RESULT_BYTES' not in ext or 'SCAN_RESULT' not in ext:
            print("no results:" % ext)
            return False
        bts = ext['SCAN_RESULT_BYTES']
        msg = ext['SCAN_RESULT']
        print(msg, bts, len(bts))
    return True


def test_009s_airplanemode():               # issue sl4a #9 {{{1
    # this cause null pointer exception in Anroid 4.4>
    droid.toggleAirplaneMode(True)
    return True


# tests for some facade {{{1
def event_loop():
  for i in range(10):
    e = droid.eventPoll(1)
    if e.result is not None:
      return True
    time.sleep(2)
  return False


def test_clipboard():
  previous = droid.getClipboard().result
  msg = 'Hello, world!'
  droid.setClipboard(msg)
  echo = droid.getClipboard().result
  droid.setClipboard(previous)
  return echo == msg


def test_gdata():
  if True:
    try:
        import gdata.docs.service

        global skip_gui
        if skip_gui:
            return True
    except:
        return False
  # Create a client class which will make HTTP requests with Google Docs server.
  client = gdata.docs.service.DocsService()

  # Authenticate using your Google Docs email address and password.
  username = droid.dialogGetInput('Username').result
  password = droid.dialogGetPassword('Password', 'For ' + username).result
  try:
    client.ClientLogin(username, password)
  except:
    return False

  # Query the server for an Atom feed containing a list of your documents.
  documents_feed = client.GetDocumentListFeed()
  # Loop through the feed and extract each document entry.
  return bool(list(documents_feed.entry))


def test_gps():
  droid.startLocating()
  try:
    return event_loop()
  finally:
    droid.stopLocating()


def test_sensors():
  droid.startSensing()
  try:
    return event_loop()
  finally:
    droid.stopSensing()


def test_speak():
  result = droid.ttsSpeak('Hello, world!')
  return result.error is None


def test_phone_state():
  droid.startTrackingPhoneState()
  try:
    return event_loop()
  finally:
    droid.stopTrackingPhoneState()


def test_ringer_silent():
  result1 = droid.toggleRingerSilentMode()
  result2 = droid.toggleRingerSilentMode()
  return result1.error is None and result2.error is None


def test_ringer_volume():
  get_result = droid.getRingerVolume()
  if get_result.error is not None:
    return False
  droid.setRingerVolume(0)
  set_result = droid.setRingerVolume(get_result.result)
  if set_result.error is not None:
    return False
  return True


def test_get_last_known_location():
  result = droid.getLastKnownLocation()
  return result.error is None


def test_geocode():
  result = droid.geocode(0.0, 0.0, 1)
  return result.error is None


def test_wifi():
  result1 = droid.toggleWifiState()
  result2 = droid.toggleWifiState()
  return result1.error is None and result2.error is None


def test_make_toast():
  result = droid.makeToast('Hello, world!')
  return result.error is None


def test_vibrate():
  result = droid.vibrate()
  return result.error is None


def test_notify():
  result = droid.notify('Test Title', 'Hello, world!')
  return result.error is None


def test_get_running_packages():
  result = droid.getRunningPackages()
  return result.error is None


# tests for USBSerialFacade {{{1
def test_usb():                                             # {{{2
    result = droid.usbserialDeviceList()
    if result.error is None:
        print(result.data)
        return True
    return False


# tests for SL4A GUI parts {{{1
def test_alert_dialog():                                    # {{{2
    global skip_gui
    if skip_gui:
        return None
    title = 'User Interface'
    message = 'Welcome to the SL4A integration test.'
    droid.dialogCreateAlert(title, message)
    droid.dialogSetPositiveButtonText('Continue')
    droid.dialogShow()
    response = droid.dialogGetResponse().result
    return True


def test__alert_dialog_with_buttons():                      # {{{2
    global skip_gui
    if skip_gui:
        return None
    title = 'Alert'
    message = ('This alert box has 3 buttons and '
               'will wait for you to press one.')
    droid.dialogCreateAlert(title, message)
    droid.dialogSetPositiveButtonText('Yes')
    droid.dialogSetNegativeButtonText('No')
    droid.dialogSetNeutralButtonText('Cancel')
    droid.dialogShow()
    response = droid.dialogGetResponse().result

    assert response['which'] in ('positive', 'negative', 'neutral')
    # print("debug:", response)
    skip_gui = response['which'] == "negative"
    return True


def test_spinner_progress():                                # {{{2
  title = 'Spinner'
  message = 'This is simple spinner progress.'
  droid.dialogCreateSpinnerProgress(title, message)
  droid.dialogShow()
  time.sleep(2)
  droid.dialogDismiss()
  return True


def test_horizontal_progress():                             # {{{2
  title = 'Horizontal'
  message = 'This is simple horizontal progress.'
  droid.dialogCreateHorizontalProgress(title, message, 50)
  droid.dialogShow()
  for x in range(0, 50):
    time.sleep(0.1)
    droid.dialogSetCurrentProgress(x)
  droid.dialogDismiss()
  return True


def test__alert_dialog_with_list():                         # {{{2
    global skip_gui
    if skip_gui:
        return None
    title = 'Alert'
    droid.dialogCreateAlert(title)
    droid.dialogSetItems(['foo', 'bar', 'baz'])
    droid.dialogShow()
    response = droid.dialogGetResponse().result

    # print("debug:", response)
    skip_gui = response.item == 1
    return True


def test__alert_dialog_with_single_choice_list():           # {{{2
    global skip_gui
    if skip_gui:
        return None
    title = 'GUI Test?'
    droid.dialogCreateAlert(title)
    droid.dialogSetSingleChoiceItems(['Continue', 'Skip', 'baz'])
    droid.dialogSetPositiveButtonText('Yay!')
    droid.dialogShow()
    response = droid.dialogGetResponse().result

    choices = droid.dialogGetSelectedItems().result
    skip_gui = 1 in choices
    return True


def test__alert_dialog_with_multi_choice_list():            # {{{2
    global skip_gui
    if skip_gui:
        return None
    title = 'Alert'
    droid.dialogCreateAlert(title)
    droid.dialogSetMultiChoiceItems(['foo', 'bar', 'baz'], [])
    droid.dialogSetPositiveButtonText('Yay!')
    droid.dialogShow()
    response = droid.dialogGetResponse().result

    choices = droid.dialogGetSelectedItems().result
    # print("debug:", choices)
    skip_gui = 1 in choices
    return True


# tests for native module {{{1
def test_ssl():
    try:
        import ssl
    except:
        return False
    # TODO: make test method
    ssl             # missing ssl extension?
    return True


def test_ctypes():
    try:
        import ctypes
    except:
        return False
    # TODO: make test method
    ctypes          # r17-22, this cause segfault error.
    return True


def test_readline():
    try:
        import readline
    except:
        return False
    # TODO: make test method
    readline
    return True


def test0_curses():                                        # {{{2
    import os
    if not os.environ.get("TERM", ""):
        os.environ["TERM"] = "vt100"
        os.environ["TERMINFO"] = ("/data/data/com.googlecode.pythonforandroid"
                                  "/files/python/share/terminfo")
    try:
        import _curses
    except:
        return False
    _curses.initscr()
    _curses.endwin()
    return True


def test_termios():
    try:
        import termios
    except:
        return False
    # TODO: make test method
    termios
    return True


def test_bz2():
    try:
        import bz2
    except:
        return False
    # TODO: make test method
    bz2
    return True


def test_expat():
    try:
        import pyexpat
    except:
        return False
    # TODO: make test method
    pyexpat
    return True


def test_sqlite3():
    try:
        import sqlite3
    except:
        return False
    # TODO: make test method
    sqlite3
    return True


# tests for pure python module {{{1
def test_bs():
    try:
        import BeautifulSoup
    except:
        return False
    # TODO: make test method
    BeautifulSoup
    return True


def test_xmpp():
    try:
        import xmpp
    except:
        return False
    # TODO: make test method
    xmpp
    return True


if __name__ == '__main__':                                  # {{{1
    def boilerplate(f):
        try:
            ret = f()
        except:
            print(traceback.format_exc())
            return False
        return ret

    fOutName = False

    seq = globals().items()
    seq = [i for i in seq if i[0].startswith("test_")]
    seq = [i for i in seq if isinstance(i[1], types.FunctionType)]
    seq.sort(key=lambda x: x[0])
    for name, value in seq:
        if fOutName:
            print('Running %s...' % name, end="")
            f = boilerplate(value)
            sys.stdout.flush()
            if f is True:
                print(' PASS')
            elif f is None:
                print(' SKIP')
            else:
                print(' FAIL')
        else:
            sys.stdout.flush()
            f = boilerplate(value)
            if f is True:
                print(".", end="")
            elif f is None:
                print("S", end="")
            else:
                print("F:%s" % name, end="")
# vi: ft=python:et:ts=4:fdm=marker

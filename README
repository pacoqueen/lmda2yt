LMDA2YT
=======

![WTFPL](http://www.wtfpl.net/wp-content/uploads/2012/12/wtfpl-badge-1.png)

> «La musiquita del amor» to YouTube

A simple script to create or update playlists in youtube based on a list of
songs in a plain text file.

## Install

This is only a "scratch your own itch" piece of software developed in short 
time to resolve my own need and learn how to play with YouTube API.

There's no installation. If you are looking for a sample script, clone this
repository and adapt the code to solve your own needs.

For instance, you may want to change the `CLIENT_SECRETS_FILE` in 
`yt_playlist.py` to point your _json_ file with your preferred name instead of 
using mine when you download your Google's credential file.

## Usage

You have to modify the _bash_ script `google_credentials.runme.sh` in order to 
point to **your own** _json_ credentials file.

Documentation about how to generate secret, credential files and access to
YouTube Data API can be found on [Google's developers center site](https://developers.google.com/youtube/v3/guides/authentication).

Create a `config.py` file. You can copy `config.sample.py` to `config.py` and
replace `"YOUR_OWN_YOUTUBE_API_DEVELOPER_KEY_HERE"` with... you know... your 
own developer key. See above link on how to get it.

```
. ./google_credentials.runme.sh
./lmda2yt.py -f input_list.txt -n "A new playlist" -d "My own very new brand playlist"
```

Format of input file has to be: `number - artist - song title`. One song for each line.

### NOTE

The playlist will be created as **private**. You have to change to public in 
your YouTube playlists page if you want to.

## LICENSE

WTFPL - Do What the Fuck You Want to Public License

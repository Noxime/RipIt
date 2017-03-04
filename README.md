# RipIt
Ripping software designed to back up entire subreddits. Won't work perfectly for
every case.

### READ THROUGH THE RIPIT.PY FILE!
There is no command line interface for now, so the script is configured there.

### Features
* Download subreddit as JSON
* Download directly linked files
* Basic support for youtube-dl (SEE BELOW)

### Planned Features
* Moving from raw JSON to formatted text
* Download media from comments
* Better youtube-dl support

##### Youtube-DL
The current support of youtube-dl is very basic as of right now. One big issue
right now is that if you have a custom youtube-dl config, downloading will most
likely fail. 

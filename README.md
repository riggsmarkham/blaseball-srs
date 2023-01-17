# blaseball-srs

An attempt to implement a simple rating system for blaseball (one that only takes into account run differential and strength of schedule).
Future updates (that'll make it less simple) are in the works.

Just run srs.py to get a printout of the ratings and run differentials.

Trying to copy the method described here: <https://web.archive.org/web/20161031224357/http://www.pro-football-reference.com/blog/index4837.html>

<https://api2.sibr.dev/mirror/games> has been very helpful in figuring out the game record api.

If you want to use this with the blaseball api (not the mirror), in order to access the api, you need to create a config.ini file in this directory, and put valid login info for blaseball into it in this format:

    [login]
    email = your_email
    password = your_password

I've also got other stuff in here (e.g. pythagorean win percentage), and I'm going to add more things that interest me.
Most of my other random stuff is in misc.py. Will I move it out of this repo? We'll see...

Season 1 Id: cd1b6714-f4de-4dfc-a030-851b3459d8d1

Modifications to make:

* Put season ids in the config file (auto-updating)
* SRS v2
  * Use some sort of regression to find best exponent for pythagorean W%
  * Figure out how to have separate offense & defense ratings in the SRS
  * Split defensive ratings by pitcher
  * Figure out variance relation of high scoring vs. low scoring environment
  * Figure out how to use that variance relation to combine offense/defense ratings properly

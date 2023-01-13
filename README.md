# blaseball-srs

An attempt to implement a simple rating system for blaseball (one that only takes into account run differential and strength of schedule).

Trying to copy the method described here: <https://web.archive.org/web/20161031224357/http://www.pro-football-reference.com/blog/index4837.html>

<https://api2.sibr.dev/mirror/games> has been very helpful in figuring out the game record api.

If you want to use this, in order to access the api, you need to create a config.ini file in this directory, and put valid login info for blaseball into it in this format:

    [login]
    email = your_email
    password = your_password

I've also got other stuff in here (e.g. pythagoren win percentage), and I'm going to add more things that interest me.

Season 1 Id: cd1b6714-f4de-4dfc-a030-851b3459d8d1

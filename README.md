# Deploying this Flask app to the cloud via Heroku

# Sign up for Heroku

Heroku, being a Software as a Service (SaaS)-type of service, requires you to create an account and login before you can start using its computers. Don't worry, creating an account and running a simple app is free and doesn't require a credit card.

You can create an account at this URL: [https://signup.heroku.com/dc](https://signup.heroku.com/dc)

## Download the Heroku toolbelt

Heroku has a command-line "toolbelt" that we must download and install in order commands that will simplify our communication with the Heroku servers. The toolbelt can be downloaded at: [https://toolbelt.heroku.com/](https://toolbelt.heroku.com/)

![image download-heroku-toolbelt.png](readme_assets/images/download-heroku-toolbelt.png)

## Authenticate with Heroku with `heroku login`

Installing the Heroku toolbelt will give you access to the `heroku` command which has several subcommands for interacting with the Heroku service. 

The first command you need to run is `heroku login`, which will ask you to enter your login credentials so that every subsequent `heroku` command knows who you are:

(You will only have to do this __once__)

~~~sh
$ heroku login
~~~

![readme_assets/images/heroku-login.gif](readme_assets/images/heroku-login.gif)

# Setting up our app's Git repo

This part will be a little confusing. Heroku deploys using __git__ -- which is _not to be confused with_ __Github__. (Hopefully, you have __git__ installed at this point.)

Basically, this means before we can deploy to Heroku, we need to create a git repo in our app, add the files, and commit them. But we _don't_ need to push them onto a Github repo if we don't want to.

In fact, for this basic app, don't bother making a Github repo. Just make a local git repo:

~~~sh
$ git init
$ git add .
$ git commit -m 'first'
~~~


# Creating a Heroku application

OK, now Heroku has all it needs to provision a server for our application.

Now we need to do two steps:

1. Tell Heroku to initialize an application [via its __create__ command](https://devcenter.heroku.com/articles/creating-apps).
2. Tell Heroku to deploy our application by pushing our code onto the Git repo hosted on Heroku.


## Initializing a Heroku application

First, make sure you've successfully created a Git repo in your app folder. Running `git status` should, at the very least, not give you an error message telling you that you've yet to create a Git repo.

Then, run this command:

~~~sh
$ heroku create
~~~

The __create__ subcommand sets up a URL that your application will live at, and a Git repo from which you'll be pushing your code to on deployment.

The `heroku create` command results in output that looks like this:

~~~stdout
Creating app... ⬢ warm-scrubland-16039
https://warm-scrubland-16039.herokuapp.com/ | https://git.heroku.com/warm-scrubland-16039.git
~~~

That output tells us two things:

1. Our application can be visited at: `https://boiling-journey-47934.herokuapp.com/`
2. Heroku has git repo at the url `https://git.heroku.com/boiling-journey-47934.git`...In fact, the `create` command has helpfully set up a _remote_ named _heroku_ for us to __push__ to.

If you visit your application's app, e.g. `https://some-funnyword-9999.herokuapp.com/`. you'll get a placeholder page:

![image welcome-heroku.png](readme_assets/images/welcome-heroku.png)

That's not what we programmed our app to do -- so that's just a page that comes from Heroku -- we haven't really deployed our app yet. But Heroku is ready for us. You can further confirm this by visiting [https://dashboard.heroku.com/](https://dashboard.heroku.com/) and seeing your application's URL at the bottom:

![image heroku-dashboard.png](/readme_assets/images/heroku-dashboard.png)

Clicking on that application entry will reveal a page that is empty of "processes":

![image heroku-dashboard-initial-app.png](readme_assets/images/heroku-dashboard-initial-app.png)


As for that Git repo that Heroku created for us...run this command to see the endpoints:

~~~sh
$ git remote show heroku
~~~

The output:

~~~sh
* remote heroku
  Fetch URL: https://git.heroku.com/warm-scrubland-16039.git
  Push  URL: https://git.heroku.com/warm-scrubland-16039.git
  HEAD branch: (unknown)
~~~



## Deploying our application code

OK, let's finally __deploy our app__. We tell Heroku that we want to deploy our currently committed code by doing a `git push` to `heroku master`:

~~~sh
$ git push heroku master
~~~

This should seem familiar to when you've pushed code to your __Github account__, but targeting `origin master`:

~~~sh
$ git push origin master
~~~

...but of course, we haven't actually created a __Github__ git repo for our simple app...we've only created a __local repo__. And, by running `heroku create`, we also created a repo on Heroku...which we will now push to:

~~~sh
$ git push heroku master
~~~

And with that simple command, Heroku will go through the steps of taking our application code, installing the dependencies we specified in `requirements.txt` and `runtime.txt`, and then starting a webserver as specified in `Procfile`:

(this process takes a lot longer than simply pushing code onto Github to save)

After about 30 seconds, you'll get output telling you how to find your application on the web:


![readme_assets/images/heroku-git-push.gif](readme_assets/images/heroku-git-push.gif)

~~~sh
remote:        https://warm-scrubland-16039.herokuapp.com/ deployed to Heroku
remote: 
remote: Verifying deploy.... done.
To https://git.heroku.com/warm-scrubland-16039.git
   1c6e386..b0e9510  master -> master
~~~

My app happens to be given the name __warm-scrubland-16039__, which means that it is now available at the following URL for the whole world:

[https://warm-scrubland-16039.herokuapp.com/](https://warm-scrubland-16039.herokuapp.com/ )

And that's how you make your application available to the world.

# Changing our application code

Altering the codebase of a Heroku-deployed app is not much different than how we've re-edited and saved code before, except that we have to run __git push heroku master__ in order to update the application on the Heroku server -- Heroku's server doesn't have a mind-meld with our computer's hard drive, we have to notify it of our changes via a `git push`.

However, `git push` doesn't push anything until we've actually changed code -- and added and committed those changes via `git add` and `git commit`.

Give it a try. Change __app.py__. Then add/commit/push:

~~~sh
git add --all
git commit -m 'changes'
git push heroku master
~~~

Depending on how much you've altered the code base, the push/deploy process may take just as long as the initial install. But that's a reasonable price to pay for an easy process for updating an application that the entire world can access.

# Managing your Heroku apps

If you plan on using Heroku to deploy your apps but _not while not paying a monthly bill_, you'll only be able to deploy one live app at a time.

To __destroy__ an app, which will destroy the deployed version and the reserved URL -- but _not_ your local code -- you can select your app via the [Heroku web dashboard](https://dashboard.heroku.com/apps), then delete it via its configuration/settings menu.

Or, if you'd rather do it from the command-line with the Heroku toolbelt, use the __apps:destroy__ subcommand:

~~~sh
$ heroku apps:destroy whatever-yourappnameis-99999
~~~

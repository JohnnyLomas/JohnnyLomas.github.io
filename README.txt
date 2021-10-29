Goals:
  1. Automatically create and maintain a weekly, daily, monthly, and yearly training log as CSV viewable in excel
     using garmin connect data
  2. Enable custom analyses for performance tracking over time
  3. Stop paying for shit I can do myself much more specifically

Dependencies:
  1. python-garminconnect

ISSUES:
  1. 3 Month Overview charts skip weeks with no data...
  2. 3 Month Overview charts split most recent two activity days up?
  3. Weekly charts have space for the 8th day back... but no data
  4. Weird issue with login... sometimes works, sometimes doesn't
	I spent some time working with the login issues. I was able to knit
	after signing out and signing back in with "Remember Me" checked.
	I had also been running a bunch of doLogin functions from the 
	python3 interpreter beforehand. I think the key here is to make 
	Garmin's security happy by using the sign-in through the web
	interface? Make sure to restart R after failed login attempts, this
	seems to help?

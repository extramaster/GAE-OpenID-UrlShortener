<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>URLShortener - Login</title>
<link rel="stylesheet" type="text/css" href="css/styles.css" media="screen">
<link rel="shortcut icon" href="">
<meta name="keywords" content="">
<meta name="description" content="">
</head>
<body>
<div id="header">
</div>
<div id="content">
<h1>Login below to create links and share!</h1>
<h2>Sign in with: </h2>
{{ provider }}
<h2>Have your own OpenID provider?</h2>
  <form method="get" action="/_ah/login_redir" style="text-align:center">
    <input type="text" name="claimid">
    <input type="submit" value="Log In">
    <input type="hidden" value="{{ master }}" name="continue">
  </form>
</div>
</body>
</html>

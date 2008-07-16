var StyleFile = "narrative" + document.cookie.charAt(6) + ".css";
document.writeln('<link href="' + StyleFile + '" rel="stylesheet" type="text/css" media="screen" />');
document.writeln('<style type="text/css">!-- narrative' + document.cookie.charAt(6) + '--></style>');

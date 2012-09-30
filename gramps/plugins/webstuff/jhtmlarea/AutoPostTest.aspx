<%@ Page Language="VB" ValidateRequest="false" AutoEventWireup="false" CodeFile="AutoPostTest.aspx.vb" Inherits="PostTest" %>

<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">

<html xmlns="http://www.w3.org/1999/xhtml">
<head id="Head1" runat="server">
    <title></title>
    <script type="text/javascript" src="scripts/jquery-1.3.2.js"></script>

    <script type="text/javascript" src="scripts/jHtmlArea-0.7.0.js"></script>
    <link rel="Stylesheet" type="text/css" href="style/jHtmlArea.css" />
    <script type="text/javascript">
        $(function() {
            $("textarea").htmlarea(); // Initialize jHtmlArea's with all default values

            //window.setTimeout(function() { $("form").submit(); }, 3000);
        });
    </script>
</head>
<body>
    <form id="form1" runat="server">
    <div>
        <asp:ScriptManager runat="server" ID="sm1"></asp:ScriptManager>
        
        <asp:Literal runat="server" ID="litText"></asp:Literal><br />
        
        <textarea runat="server" id="txtText" cols="50" rows="15"></textarea>
        <input type="submit" value='manual submit' />  
        <br />
        
        <asp:Button runat="server" ID="btnSubmit" Text="asp:Button" />
        <asp:LinkButton runat="server" ID="lbSubmit" Text="asp:LinkButton"></asp:LinkButton>
    </div>
    </form>
</body>
</html>

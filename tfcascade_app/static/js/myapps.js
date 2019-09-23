function update_job_status(cur_url, next_url)
    {
    //alert(cur_url + "<br />" + next_url);
    var ajaxObj;
    try
        {
        ajaxObj = new XMLHttpRequest();
        }
    catch (e)
        {
        try
            {
            ajaxObj = new ActiveXObject("Msxml2.XMLHTTP");
            }
        catch (e)
            {
            try
                {
                ajaxObj = new ActiveXObject("Microsoft.XMLHTTP");
                }
            catch (e)
                {
                alert("Your browser does not support AJAX!");
                return false;
                }
            }
        }
    ajaxObj.onreadystatechange = function()
        {
            //alert('send');
        if (ajaxObj.readyState == 4)
            {
                //alert(ajaxObj.responseText);
            if (ajaxObj.responseText=='SUCCESS')
                {
                document.getElementById('error_msg').innerHTML="Success";
                show_modal(next_url);
                document.getElementById('need_reload').value=1;
                }
            else
                {
                document.getElementById('error_msg').innerHTML="Failed";
                }
            }
        else
            {
            document.getElementById('error_msg').innerHTML="<img width='35px' height='35px' src='/pimadb/images/loading48.gif'>";
            }
        }
    ajaxObj.open("GET", cur_url, true);
    ajaxObj.send(null);
    return false;     
    }
    
function show_modal(cur_url)
    {
    try
        {
        document.getElementById('need_reload').value=0;
        }
    catch (e)
        {
            
        }
    
    //alert('in check stat');
    var ajaxObj;
    try
        {
        ajaxObj = new XMLHttpRequest();
        }
    catch (e)
        {
        try
            {
            ajaxObj = new ActiveXObject("Msxml2.XMLHTTP");
            }
        catch (e)
            {
            try
                {
                ajaxObj = new ActiveXObject("Microsoft.XMLHTTP");
                }
            catch (e)
                {
                alert("Your browser does not support AJAX!");
                return false;
                }
            }
        }
        
    $('#myModal .modal-body').html("<img width='35px' height='35px' src='/pimadb/images/loading48.gif'>");
    $('#myModal').modal('show', {backdrop: 'static'});
    
    ajaxObj.onreadystatechange = function()
        {
        if (ajaxObj.readyState == 4)
            {
            disp_str = '';
            disp_str = "<div id='int_res_modal_inner_div'>";
            disp_str += ajaxObj.responseText;
            disp_str += "</div>";
            $('#myModal .modal-body').html(disp_str);
            }
        else
            {
            $('#myModal .modal-body').html("<img width='35px' height='35px' src='/pimadb/images/loading48.gif'>");
            }
        }
    ajaxObj.open("GET", cur_url,true);
    ajaxObj.send(null);
    return false;
    }
function show_add_new_modal(cur_url)
    {
    document.getElementById('need_reload').value=0;
    //alert('in check stat');
    var ajaxObj;
    try
        {
        ajaxObj = new XMLHttpRequest();
        }
    catch (e)
        {
        try
            {
            ajaxObj = new ActiveXObject("Msxml2.XMLHTTP");
            }
        catch (e)
            {
            try
                {
                ajaxObj = new ActiveXObject("Microsoft.XMLHTTP");
                }
            catch (e)
                {
                alert("Your browser does not support AJAX!");
                return false;
                }
            }
        }
        
    $('#addnew_Modal .modal-body').html("<img width='35px' height='35px' src='/pimadb/images/loading48.gif'>");
    $('#addnew_Modal').modal('show', {backdrop: 'static'});
    
    ajaxObj.onreadystatechange = function()
        {
        if (ajaxObj.readyState == 4)
            {
            disp_str = '';
            disp_str = "<div id='int_res_modal_inner_div'>";
            disp_str += ajaxObj.responseText;
            disp_str += "</div>";
            $('#addnew_Modal .modal-body').html(disp_str);
            try
                {
                document.getElementById('need_reload').value=1;
                }
            catch (e)
                {
                    
                }
            }
        else
            {
            $('#addnew_Modal .modal-body').html("<img width='35px' height='35px' src='/pimadb/images/loading48.gif'>");
            }
        }
    ajaxObj.open("GET", cur_url,true);
    ajaxObj.send(null);
    return false;
    }
    
function submit_form_ajax(form)
    {
    //alert(cur_url + "<br />" + next_url);
    var ajaxObj;
    try
        {
        ajaxObj = new XMLHttpRequest();
        }
    catch (e)
        {
        try
            {
            ajaxObj = new ActiveXObject("Msxml2.XMLHTTP");
            }
        catch (e)
            {
            try
                {
                ajaxObj = new ActiveXObject("Microsoft.XMLHTTP");
                }
            catch (e)
                {
                alert("Your browser does not support AJAX!");
                return false;
                }
            }
        }
    ajaxObj.onreadystatechange = function()
        {
            //alert('send');
        if (ajaxObj.readyState == 4)
            {
                //alert(ajaxObj.responseText);
            if (ajaxObj.responseText=='SUCCESS')
                {
                document.getElementById('error_msg').innerHTML="Success";
                show_modal(next_url);
                document.getElementById('need_reload').value=1;
                }
            else
                {
                document.getElementById('error_msg').innerHTML="Failed";
                }
            }
        else
            {
            document.getElementById('error_msg').innerHTML="<img width='35px' height='35px' src='/pimadb/images/loading48.gif'>";
            }
        }
    ajaxObj.open("GET", cur_url, true);
    ajaxObj.send(null);
    return false;     
    }

function search() {
    document.getElementById("search_form").submit();
}
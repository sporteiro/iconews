class Main {
    constructor() {
        this.country_list;
    }
    init()  {
        this.country_list = this.get_contries();
        this.select_contries();
    }
    get_contries()  {
        var country_list;
        var url = "http://localhost:8011/iconoticias/php/main.php?country_list=1";
        $.ajax({
            url: url,
            type: 'get',
            dataType: "html",
            async: false,
            success: function(data) {
                country_list = data;
            },
            error: function (xhr, ajaxOptions, thrownError) {
                console.log(xhr.status);
                console.log(thrownError);
            }
        });
        return country_list;
    }
    select_contries()   {
        var countries = JSON.parse(this.country_list);
        $.each(countries, function (k,v) {
            var country = k;
            var option = '<option value="'+country+'" style="background-image:url(img/'+country+'_mini.png);" data-image="img/'+country+'_mini.png">'+country+'</option>';
            $("#select_country").append(option);
        });
    }
    change_country()    {
        var selected_country = $( "#select_country option:selected" ).text();
        var country_news = JSON.parse(this.get_news_from_country(selected_country));
        console.log("country_news channel",country_news["channel"]);
        this.display_country_news(country_news["channel"]);
    }
    get_news_from_country(country)  {
        var country_news;
        var url = "http://localhost:8011/iconoticias/php/main.php?country="+country;
        $.ajax({
            url: url,
            type: 'get',
            dataType: "html",
            async: false,
            success: function(data) {
                country_news = data;
            },
            error: function (xhr, ajaxOptions, thrownError) {
                console.log(xhr.status);
                console.log(thrownError);
            }
        });
        console.log("country_news: ",country_news);
        return country_news;
    }
    display_country_news(channel)  {
        $("#titulares").html("");
        $.each(channel["item"], function (i) {
            console.log("channel ",channel["item"][i]["title"]);           
            var title = channel["item"][i]["title"];
            var title_words = title.split(" ");
            var description = channel["item"][i]["description"];
            var icons = "";
            $.each(title_words, function (i) {
                //icons += "<img src='"+main.search_icons(title_words[i])+"' width='20%'/>";
                icons += main.search_icons(title_words[i]);
            });
            console.log("icons: ",icons);
            var html = "<div class='noticia'><div class='cadaNoticia'>"+title+"<br/>"+icons+"<div class='mas'> + </div><div class='ampliado'>"+description+"</div></div>";
            $("#titulares").append(html);
            $('.ampliado').hide();
        });
	    $('.mas').click(function() {
            console.log("mas click");
	        //$('.ampliado').show();
         	//$('.ampliado').slideDown('fast');
	        if($(this).next().is(':hidden') == true) {
    	        console.log("estaba oculto click");
		        $(this).next().slideDown('fast');
            }
	        else if($(this).next().is(':hidden') == false) {
    	        console.log("estaba visible click");
		        $(this).next().slideUp('fast');
            } 		  
         });

    }
    search_icons(word)  {
        var url = "http://localhost:8011/iconoticias/php/main.php?icons";
        var icon;
        $.ajax({
            url: url,
            type: 'get',
            dataType: "html",
            async: false,
            success: function(data) {
                data = JSON.parse(data);
               // console.log("icon_list: ",data);
                console.log("Checking word: ",word);
                if (data.includes(word+".svg")==true)   {
                    console.log("word existe en array : ",word);
                    icon = true;
                }
                else icon = false;
                
            },
            error: function (xhr, ajaxOptions, thrownError) {
                console.log(xhr.status);
                console.log(thrownError);
                icon = false;
            }
        });
        console.log("icon: ",icon);
        if (icon==true)  {
            var img = "<img src='fontawesome/"+word+".svg' width='10%'/>";
            return img;
        }
        else    {
            return " ";
        }

    }
}
main = new Main();
main.init();

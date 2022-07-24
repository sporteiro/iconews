class Main {
    constructor() {
        this.country_list;
        this.selected_country;
    }
    init()  {
        this.country_list = this.get_contries();
        this.selected_country = $( "#select_country option:selected" ).text();
        //prevents dropdown from multiple change, but also trigger only when the value is different
        $(document).ready(function () {
            $("#select_country").change(function () {
                var now_selected_country = $( "#select_country option:selected" ).text();
                if (now_selected_country!=this.selected_country)    {
                    console.log("select_country changed to", now_selected_country);
                    this.selected_country = now_selected_country;
                    main.get_news_from_country(now_selected_country);
                }
                else    {
                    console.log("select_country did not change");
                }
            });
        });
        //show to debug
        $("#app_info").hide();
    }
    get_contries()  {
        $("#app_info").html("get_contries");
        var country_list;
        var url = "http://localhost:8011/iconoticias/php/main.php?country_list=1";
        $.ajax({
            url: url,
            type: 'get',
            dataType: "html",
            success: function(data) {
                country_list = data;
                main.make_country_select(country_list);
            },
            error: function (xhr, ajaxOptions, thrownError) {
                console.log(xhr.status);
                console.log(thrownError);
            }
        });
        return country_list;
    }
    make_country_select(country_list)   {
        $("#app_info").html("make_country_select");
        var countries = JSON.parse(country_list);
        $.each(countries, function (k,v) {
            var country = k;
            var option = '<option value="'+country+'" data-image="country-flags-main/svg/'+countries[k]['short']+'.svg">'+country+'</option>';
            $("#select_country").append(option);
        });
    }
    get_news_from_country(country)  {
        console.log("get_news_from_country",country);
        $("#app_info").html("get_news_from_country",country);
        var country_news;
        var url = "http://localhost:8011/iconoticias/php/main.php?country="+country;
        $.ajax({
            url: url,
            type: 'get',
            dataType: "html",
            success: function(data) {
                $("#app_info").html("get_news_from_country data",data);
                country_news = data;
                var country_news_JSON = JSON.parse(country_news);
                main.display_country_news(country_news_JSON["channel"]);
                
            },
            error: function (xhr, ajaxOptions, thrownError) {
                console.log(xhr.status);
                console.log(thrownError);
            }
        });
        return country_news;
    }
    display_country_news(channel)  {
        $("#app_info").html("display_country_news",channel);
        console.log("display_country_news",channel);
        $("#titulares").html("");
        $.each(channel["item"], function (i) {
            var title = channel["item"][i]["title"];
            var title_words = title.split(" ");
            var description = channel["item"][i]["description"];
            var icons = "";
            $.each(title_words, function (j) {
                main.search_icons(title_words[j],i);
            });
            var html = "<div class='noticia' id='noticia_"+i+"'><div class='cadaNoticia'>"+title+"<br/><p id='icons_"+i+"'></p><div class='mas'> + </div><div class='ampliado'>"+description+"</div></div>";
            $("#titulares").append(html);
            $('.ampliado').hide();
        });
	    $('.mas').click(function() {
	        if($(this).next().is(':hidden') == true) {
		        $(this).next().slideDown('fast');
            }
	        else if($(this).next().is(':hidden') == false) {
		        $(this).next().slideUp('fast');
            } 		  
         });

    }
    search_icons(word,id)  {
        $("#app_info").html("searching icons");
        var url = "http://localhost:8011/iconoticias/php/main.php?icons";
        var icon;
        $.ajax({
            url: url,
            type: 'get',
            dataType: "html",
            success: function(data) {
                data = JSON.parse(data);
                if (data.includes(word+".svg")==true)   {
                    //console.log("icon for this word exists : ",word, " id of the new: ",id);
                    icon = true;
                    $("#icons_"+id).append("<img src='fontawesome/"+word+".svg' width='10%'/>");
                }
                else icon = false;
                
            },
            error: function (xhr, ajaxOptions, thrownError) {
                console.log(xhr.status);
                console.log(thrownError);
                icon = false;
            }
        });
    }
}
main = new Main();
main.init();

class Main {
    constructor() {
        this.country_list = [];
        this.selected_country = null;
    }

    init() {
        this.get_countries();
        let self = this;
        $(document).ready(function () {
            $("#select_country").change(function () {
                let now_code = $(this).val();
                if (now_code !== self.selected_country) {
                    self.selected_country = now_code;
                    self.get_news_from_country(now_code);
                }
            });
        });
        $("#app_info").hide();
    }

    get_countries() {
        $.ajax({
            url: '/countries',
            type: 'GET',
            dataType: 'json',
            success: function (data) {
                main.country_list = data;
                main.build_country_select(data);
            },
            error: function (xhr, status, error) {
                console.log(xhr.status, error);
            }
        });
    }

    build_country_select(countries) {
        $("#select_country").empty();
        $.each(countries, function (i, country) {
            let option = '<option value="' + country.code + '">' + country.name + '</option>';
            $("#select_country").append(option);
        });
        // Trigger news for the first country
        if (countries.length > 0) {
            $("#select_country").val(countries[0].code);
            main.selected_country = countries[0].code;
            main.get_news_from_country(countries[0].code);
        }
    }

    get_news_from_country(country_code) {
        $.ajax({
            url: '/news?cc=' + country_code,
            type: 'GET',
            dataType: 'json',
            success: function (data) {
                main.display_news(data);
            },
            error: function (xhr, status, error) {
                console.log(xhr.status, error);
            }
        });
    }

    display_news(items) {
        $("#titulares").empty();
        if (!items || items.length === 0) {
            $("#titulares").html("<p>No news found.</p>");
            return;
        }

        $.each(items, function (i, item) {
        let title = item.title;
        let description = item.description || "";
        let icon_container = "<span id='icons_" + i + "'></span>";

        let html = `<div class='noticia' id='noticia_${i}'>
                    <div class='cadaNoticia'>
                        ${title}<br/>
                        ${icon_container}
                        <div class='mas'> + </div>
                        <div class='ampliado'>${description}</div>
                    </div>
                </div>`;
        $("#titulares").append(html);

        // Now the element exists, add icons
        let title_words = title.split(" ");
        title_words.forEach(function (word) {
            main.add_icon(word, i);
        });
    });

        $('.ampliado').hide();
        $('.mas').off('click').on('click', function () {
            $(this).next('.ampliado').slideToggle('fast');
        });
    }

    add_icon(word, news_id) {
        // Normalize word: remove accents, replace ñ, keep alphanumeric only
        let clean = word
            .normalize("NFD")                // separate base letter from accent
            .replace(/[\u0300-\u036f]/g, "") // remove accent marks
            .replace(/ñ/g, "n")
            .replace(/Ñ/g, "N")
            .replace(/[^\w]/g, "");          // remove non-word chars (punctuation, etc.)
        
        if (clean.length === 0) return;

        let img = $("<img>").attr({
            src: 'img/' + clean + '.png',
            width: '10%',
            alt: clean
        }).on('error', function () {
            $(this).remove();
        });

        $("#icons_" + news_id).append(img);
    }
}

main = new Main();
main.init();
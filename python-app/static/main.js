class Main {
    constructor() {
        this.country_list = [];
        this.selected_country = null;
    }

    init() {
        this.get_countries();
        $("#app_info").hide();

        // Close dropdown when clicking outside
        $(document).on('click', function(e) {
            if (!$(e.target).closest('.custom-dropdown').length) {
                $('.custom-dropdown').removeClass('open');
            }
        });
    }

    get_countries() {
        $.ajax({
            url: '/countries',
            type: 'GET',
            dataType: 'json',
            success: function (data) {
                main.country_list = data;
                main.build_custom_dropdown(data);
            },
            error: function (xhr, status, error) {
                console.log(xhr.status, error);
            }
        });
    }

    build_custom_dropdown(countries) {
        var self = this;
        var $selectContainer = $('#select_country').parent(); // El div.country-selector
        var $select = $('#select_country');
        $select.hide(); // Ocultamos el select nativo

        // Creamos el dropdown personalizado
        var $dropdown = $('<div class="custom-dropdown"></div>');
        var $trigger = $('<div class="custom-dropdown-trigger"></div>');
        var $list = $('<div class="custom-dropdown-list"></div>');

        // Llenamos con los datos de países
        $.each(countries, function(i, country) {
            var flagPath = 'country-flags-main/svg/' + country.code.toLowerCase() + '.svg';
            var $item = $('<div class="custom-dropdown-item" data-value="' + country.code + '">' +
                '<img src="' + flagPath + '" alt="' + country.name + '">' +
                '<span>' + country.name + '</span>' +
                '</div>');

            $item.on('click', function() {
                var value = $(this).data('value');
                if (value !== self.selected_country) {
                    self.selected_country = value;
                    self.get_news_from_country(value);
                    // Actualizar el trigger
                    $trigger.html($(this).html());
                    $dropdown.removeClass('open');
                }
            });

            $list.append($item);

            // Seleccionar el primero por defecto
            if (i === 0) {
                $trigger.html('<img src="' + flagPath + '" alt="' + country.name + '"><span>' + country.name + '</span>');
                self.selected_country = country.code;
                self.get_news_from_country(country.code);
            }
        });

        // Evento toggle del dropdown
        $trigger.on('click', function(e) {
            e.stopPropagation();
            $(this).parent().toggleClass('open');
        });

        $dropdown.append($trigger);
        $dropdown.append($list);
        $selectContainer.append($dropdown);
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
        let clean = word
            .normalize("NFD")
            .replace(/[\u0300-\u036f]/g, "")
            .replace(/ñ/g, "n")
            .replace(/Ñ/g, "N")
            .replace(/[^\w]/g, "");

        if (clean.length === 0) return;

        $.getJSON(`/get-icon/${clean}`, function (data) {
            if (data.source === 'local') {
                let img = $("<img>").attr({
                    src: data.url,
                    width: '10%',
                    alt: clean
                });
                $("#icons_" + news_id).append(img);
            } else {
                $.getJSON(`https://api.iconify.design/search?query=${data.query}&limit=1`, function (iconData) {
                    if (iconData.icons && iconData.icons.length > 0) {
                        let iconName = iconData.icons[0];
                        let svgUrl = `https://api.iconify.design/${iconName}.svg?height=24`;
                        let img = $("<img>").attr({
                            src: svgUrl,
                            width: '10%',
                            alt: clean,
                            title: `Icono para "${word}" vía Iconify`
                        });
                        $("#icons_" + news_id).append(img);
                    }
                });
            }
        });
    }
}

main = new Main();
main.init();
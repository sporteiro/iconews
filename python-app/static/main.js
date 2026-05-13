class Main {
    constructor() {
        this.country_list = [];
        this.selected_country = null;
        this.aiQueue = [];
        this.aiProcessing = false;
        this.currentAiRequest = null;
    }

    init() {
        this.get_countries();
        $("#app_info").hide();

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
        var $selectContainer = $('#select_country').parent();
        var $select = $('#select_country');
        $select.hide();

        var $dropdown = $('<div class="custom-dropdown"></div>');
        var $trigger = $('<div class="custom-dropdown-trigger"></div>');
        var $list = $('<div class="custom-dropdown-list"></div>');

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
                    $trigger.html($(this).html());
                    $dropdown.removeClass('open');
                }
            });

            $list.append($item);

            if (i === 0) {
                $trigger.html('<img src="' + flagPath + '" alt="' + country.name + '"><span>' + country.name + '</span>');
                self.selected_country = country.code;
                self.get_news_from_country(country.code);
            }
        });

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

        // Cancel any ongoing AI request and clear queue
        if (this.currentAiRequest && this.currentAiRequest.readyState !== 4) {
            this.currentAiRequest.abort();
        }
        this.currentAiRequest = null;
        this.aiQueue = [];
        this.aiProcessing = false;

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

            main.add_icons_from_words(title, i);
            main.aiQueue.push({ title: title, news_id: i });
        });

        $('.ampliado').hide();
        $('.mas').off('click').on('click', function () {
            $(this).next('.ampliado').slideToggle('fast');
        });

        this.processNextAi();
    }

    processNextAi() {
        if (this.aiQueue.length === 0 || this.aiProcessing) return;
        this.aiProcessing = true;

        var next = this.aiQueue.shift();
        var self = this;

        // Show status text
        $('#icons_' + next.news_id).append('<span class="ai-calculating">enhancing icons...</span>');

        this.currentAiRequest = $.getJSON('/ai-icons?title=' + encodeURIComponent(next.title))
            .done(function(data) {
                // Abort if the element no longer exists (country changed)
                if ($('#icons_' + next.news_id).length === 0) return;
                $('#icons_' + next.news_id + ' .ai-calculating').remove();

                if (data.keywords && data.keywords.length > 0) {
                    $('#icons_' + next.news_id).empty();
                    $.each(data.keywords, function(idx, keyword) {
                        self.add_icon(keyword, next.news_id);
                    });
                }
            })
            .fail(function(xhr, status) {
                if (status === 'abort') return;
                if ($('#icons_' + next.news_id).length === 0) return;
                $('#icons_' + next.news_id + ' .ai-calculating').remove();
            })
            .always(function() {
                if ($('#icons_' + next.news_id).length === 0) {
                    self.aiProcessing = false;
                    self.currentAiRequest = null;
                    return;
                }
                self.aiProcessing = false;
                self.currentAiRequest = null;
                self.processNextAi();
            });
    }

    add_icons_from_words(title, news_id) {
        let title_words = title.split(" ");
        title_words.forEach(function (word) {
            main.add_icon(word, news_id);
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
                        let svgUrl = `https://api.iconify.design/${iconName}.svg?height=64`;
                        let img = $("<img>").attr({
                            src: svgUrl,
                            width: '10%',
                            alt: clean,
                            title: 'Icon via Iconify'
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
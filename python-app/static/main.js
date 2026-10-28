class Main {
    constructor() {
        this.country_list = [];
        this.selected_country = null;
        this.iconQueue = [];
        this.iconProcessing = false;
        this.aiQueue = [];
        this.aiProcessing = false;
        this.currentIconRequests = {};
        this.currentAiRequest = null;
        this.newsTitles = {};
        this.runId = 0;
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
        var self = this;

        this.runId++;
        var runId = this.runId;

        if (this.currentAiRequest) {
            try { this.currentAiRequest.abort(); } catch(e) {}
        }
        this.currentAiRequest = null;

        for (let k in this.currentIconRequests) {
            try { this.currentIconRequests[k].abort(); } catch(e) {}
        }
        this.currentIconRequests = {};

        this.iconQueue = [];
        this.iconProcessing = false;
        this.aiQueue = [];
        this.aiProcessing = false;
        this.newsTitles = {};

        $("#titulares").empty();

        if (!items || items.length === 0) {
            $("#titulares").html("<p>No news found.</p>");
            return;
        }

        $.each(items, function(i, item) {
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

            self.newsTitles[i] = title;
            self.iconQueue.push({ news_id: i });
        });

        $('.ampliado').hide();
        $('.mas').off('click').on('click', function() {
            $(this).next('.ampliado').slideToggle('fast');
        });

        this.processNextIconNews(runId);
    }

    normalize_word(word) {
        return word
            .normalize("NFD")
            .replace(/[\u0300-\u036f]/g, "")
            .replace(/ñ/g, "n")
            .replace(/Ñ/g, "N")
            .replace(/[^\w]/g, "");
    }

    processNextIconNews(runId) {
        if (runId !== this.runId) return;
        if (this.iconQueue.length === 0 || this.iconProcessing) return;
        this.iconProcessing = true;

        var next = this.iconQueue.shift();
        var self = this;
        var news_id = next.news_id;
        var title = this.newsTitles[news_id];

        $('#icons_' + news_id).append('<span class="ai-calculating loading-icons">loading icons...</span>');

        let words = title.split(" ");
        let validWords = [];
        for (let i = 0; i < words.length; i++) {
            if (this.normalize_word(words[i]).length > 0) {
                validWords.push(words[i]);
            }
        }

        if (validWords.length === 0) {
            this.finish_word_icons(news_id, runId);
            return;
        }

        let pending = validWords.length;
        let completed = 0;

        $.each(validWords, function(idx, word) {
            self.fetch_word_icon(word, news_id, runId, function() {
                if (runId !== self.runId) return;
                completed++;
                if (completed >= pending) {
                    self.finish_word_icons(news_id, runId);
                }
            });
        });
    }

    finish_word_icons(news_id, runId) {
        if (runId !== this.runId) return;
        if ($('#icons_' + news_id).length === 0) return;

        $('#icons_' + news_id + ' .loading-icons').remove();
        this.iconProcessing = false;

        this.aiQueue.push({ news_id: news_id });
        this.processNextAi(runId);
        this.processNextIconNews(runId);
    }

    fetch_word_icon(word, news_id, runId, onDone) {
        var self = this;
        let clean = this.normalize_word(word);

        if (clean.length === 0) {
            if (onDone) onDone();
            return;
        }

        var requestKey = 'w_' + clean + '_' + news_id + '_' + Math.random().toString(36).substr(2, 9);

        var request = $.ajax({
            url: '/get-icon/' + encodeURIComponent(clean),
            type: 'GET',
            dataType: 'json',
            success: function(data) {
                if (runId !== self.runId) return;
                if ($('#icons_' + news_id).length === 0) return;
                self.append_icon(data, clean, news_id);
            },
            complete: function() {
                delete self.currentIconRequests[requestKey];
                if (onDone) onDone();
            }
        });

        this.currentIconRequests[requestKey] = request;
    }

    append_icon(data, clean, news_id) {
        if (data.source === 'local' || data.source === 'cached') {
            let img = $("<img>").attr({
                src: data.url,
                width: '10%',
                alt: clean
            });
            $("#icons_" + news_id).append(img);
        } else if (data.source === 'fontawesome') {
            let icon = $("<i>").attr({
                class: data.class,
                style: 'font-size: 24px; margin-right: 8px;'
            });
            $("#icons_" + news_id).append(icon);
        }
    }

    processNextAi(runId) {
        if (runId !== this.runId) return;
        if (this.aiQueue.length === 0 || this.aiProcessing) return;
        this.aiProcessing = true;

        var next = this.aiQueue.shift();
        var self = this;
        var news_id = next.news_id;
        var title = this.newsTitles[news_id];

        $('#icons_' + news_id).append('<span class="ai-calculating enhancing-icons">enhancing icons...</span>');

        this.currentAiRequest = $.ajax({
            url: '/ai-icons?title=' + encodeURIComponent(title),
            type: 'GET',
            dataType: 'json',
            success: function(data) {
                if (runId !== self.runId) return;
                if ($('#icons_' + news_id).length === 0) {
                    self.finish_ai(news_id, runId);
                    return;
                }

                $('#icons_' + news_id + ' .enhancing-icons').remove();

                let keywords = (data.keywords || []).filter(function(k) {
                    return self.normalize_word(k).length > 0;
                });

                if (keywords.length > 0) {
                    $('#icons_' + news_id).append('<span class="ai-calculating loading-enhanced">loading enhanced icons...</span>');
                    $('#icons_' + news_id).children('img, i').remove();

                    let pending = keywords.length;
                    let completed = 0;

                    $.each(keywords, function(idx, keyword) {
                        self.fetch_word_icon(keyword, news_id, runId, function() {
                            if (runId !== self.runId) return;
                            completed++;
                            if (completed >= pending) {
                                $('#icons_' + news_id + ' .loading-enhanced').remove();
                                self.finish_ai(news_id, runId);
                            }
                        });
                    });
                } else {
                    self.finish_ai(news_id, runId);
                }
            },
            error: function(xhr, status) {
                if (status === 'abort') return;
                if (runId !== self.runId) return;
                $('#icons_' + news_id + ' .enhancing-icons').remove();
                self.finish_ai(news_id, runId);
            }
        });
    }

    finish_ai(news_id, runId) {
        if (runId !== this.runId) return;
        this.aiProcessing = false;
        this.currentAiRequest = null;
        this.processNextAi(runId);
    }
}

main = new Main();
main.init();
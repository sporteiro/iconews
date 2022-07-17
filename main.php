<?php
/*
Sebastian Porteiro 2022
*/
class Main {
    private $icon_path = "fontawesome";
    public $country;
    public $country_list = ["Argentina"=>"https://news.google.com.ar/news/feeds?pz=1&cf=all&ned=es_ar&hl=es&output=rss",
                            "Colombia"=>"http://news.google.com/news?cf=all&ned=es_co&hl=en&output=rss",
                            "Cuba"=>"http://news.google.com.ar/news?cf=all&ned=es_cu&hl=es&output=rss",
                            "Uruguay"=>"http://www.elobservador.com.uy/rss/nacional/",
                            "Mexico"=>"http://news.google.com.mx/news?pz=1&cf=all&ned=es_mx&hl=es&output=rss",
                            "Poland"=>"http://news.google.com/news?cf=all&ned=en_po&hl=en&output=rss",
                            "Venezuela"=>"http://news.google.com.ar/news?cf=all&ned=es_ve&hl=es&output=rss"
                           ];

   
    function handle_request() {
        if(isset($_GET['country_list'])) {
    	     $response = $this->country_list;
        }
        else if(isset($_GET['country'])) {
    	     $response = $this->show_feed_from_country($_GET['country']);
        }
        else if(isset($_GET['icons'])) {
    	     $response = $this->get_icon_list($_GET['country']);
        }
    	return json_encode($response);
    }
    function show_feed_from_country($country)   {
        $url = $this->country_list[$country];
        $feed = implode(file($url));
        $xml = simplexml_load_string($feed);
        return $xml;
    }
    function get_icon_list()   {
        $icon_list  = scandir($this->icon_path);
        return $icon_list;
    }
    
}
$main = new Main;
echo $main->handle_request();
?>



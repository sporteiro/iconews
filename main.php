<?php
/*
Sebastian Porteiro 2022
*/
class Main {
    private $icon_path = "fontawesome";
    public $country;
    public $country_list = ["Argentina"=>["rss"=>"https://news.google.com/rss/headlines/section/topic/NATION?hl=en-US&gl=AR&ceid=AR:en","short"=>"ar"],
                            "Colombia"=>["rss"=>"https://news.google.com/rss/headlines/section/topic/NATION?hl=en-US&gl=CO&ceid=CO:en","short"=>"co"],
                            "Cuba"=>["rss"=>"https://news.google.com/rss/headlines/section/topic/NATION?hl=en-US&gl=CU&ceid=CU:en","short"=>"cu"],
                            "Mexico"=>["rss"=>"https://news.google.com/rss/headlines/section/topic/NATION?hl=en-US&gl=MXR&ceid=MX:en","short"=>"mx"],
                            "Poland"=>["rss"=>"https://news.google.com/rss/headlines/section/topic/NATION?hl=en-US&gl=PL&ceid=PL:en","short"=>"pl"],
                            "Spain"=>["rss"=>"https://news.google.com/rss/headlines/section/topic/NATION?hl=en-US&gl=ES&ceid=ES:en","short"=>"es"],
                            "Venezuela"=>["rss"=>"https://news.google.com/rss/headlines/section/topic/NATION?hl=en-US&gl=VE&ceid=VE:en","short"=>"ve"],
                            "Uruguay"=>["rss"=>"https://news.google.com/rss/headlines/section/topic/NATION?hl=en-US&gl=UY&ceid=UY:en","short"=>"uy"],
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
        $url = $this->country_list[$country]['rss'];
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



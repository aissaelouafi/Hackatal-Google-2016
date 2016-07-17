console.log("Aissa");
d1p_fr = ["L'arbitre donne le coup d'envoi du match ! ","C'est parti entre $PAYS1 et $PAYS2 ! ","Coup d'envoi du match entre $PAYS1 et $PAYS2! ","Début du match entre $PAYS1 et $PAYS2 ! ","Début de la premiere période ! ","C'est parti entre $PAYS1 et $PAYS2 !"];
d2p_fr = ["L'arbitre donne le coup d'envoie de la deuxieme période","Début de la deuxiéme période","C'est parti pour la deuxieme mi-temps","Début de la seconde période !","Les joueurs sont de retour sur la pelouse ! "];
but_fr = ["Buuuuut pour $JOUEUR !","Goooal pour $JOUEUR !!","But pour $JOUEUR !!","$JOUEUR marque un but fantastique ! "];
cgt_fr = ["Changement de $PLAYER1 par $PLAYER2","Sortie de $PLAYER1 remplacé par $PLAYER2","Sortie de $PLAYER1 et entrée de $PLAYER2"];
cja_fr = ["Un jaune pour $JOUEUR","$JOUEUR prend un jaune ! Il doit se méfier afin d'éviter un rouge ! ","Carton jaune pour le joueur $JOUEUR","Avertissement pour $JOUEUR ","Carte jaune contre $JOUEUR"];
cro_fr = ["Carton rouge pour le joueur $JOUEUR","Suspension du joueur $JOUEUR"];
pen_fr = ["Penalty pour $COUNTRY","Tir au but pour $COUNTRY"];
tir_fr = ["Tir de $JOUEUR ! ","Une frappe de $JOUEUR ! ","$JOUEUR met une frappe "];
f1p_fr = ["Fin de la premiere période entre $PAYS1 et $PAYS2","Fin des premieres 45 minutes entre $PAYS1 et $PAYS2"];
f2p_fr = ["Fin de la deuxieme periode","Fin du match","C'est fini entre $PAYS1 et $PAYS2"];

var team1 = '';
var team2 = '';
Array.prototype.sample = function(){
  return this[Math.floor(Math.random()*this.length)];
}

// Get file actuality
$.getJSON(my_json_file,function(data){
    console.log(data);

    $.each( data, function( key, val ) {
        var eq1 = data['header'].eq1;
        eq1 = eq1.replace(/~/g,' ');
        eq1 = eq1.replace(/-/g,' ');
        team1 = eq1;


        var eq2 = data['header'].eq2;
        eq2 = eq2.replace(/~/g,' ');
        eq2 = eq2.replace(/-/g,' ');
        team2 = eq2;

        if(key == 'header') return;

        var $array_body = $('.tbody');
        var date = val.date;
        var event = val.event;
        var info = val.info;

        // joueurs :
        var joueur1 = info.substr(0, info.indexOf(';'));
        var joueur2 = info.split(";").pop();

        var matching = {"D1P":d1p_fr,"D2P":d2p_fr,"BUT":but_fr,"CGT":cgt_fr,"CJA":cja_fr,"CRO":cro_fr,"PEN":pen_fr,"TIR":tir_fr,"F1P":f1p_fr,"F2P":f2p_fr};
        var phrase_description = matching[val.event].sample();
        phrase_description = phrase_description.replace('$JOUEUR','<b>'+info+'</b>')
        phrase_description = phrase_description.replace('$COUNTRY','<b>'+info+'</b>')
        phrase_description = phrase_description.replace('$PAYS1','<b>'+eq1+'</b>')
        phrase_description = phrase_description.replace('$PAYS2','<b>'+eq2+'</b>')
        phrase_description = phrase_description.replace('$PLAYER1','<b>'+joueur1+'</b>')
        phrase_description = phrase_description.replace('$PLAYER2','<b>'+joueur2+'</b>')
        var row = "<tr><td id='time'><p>"+date+"</p></td><td id='description'><hr class='big'><img id='event_icon' src='./img/events/"+event+".png'>  "+phrase_description+"</td><hr class='small'>";
        $array_body.append(row);

    });


    // Get team players
    $.getJSON("./json/players.json",function(data){
        data_team1 = data[team1];
        data_team2 = data[team2];
        $('#team1_name').text(team1);
        $('#team2_name').text(team2);
        console.log("Islande player ");
        console.log(data_team1);
        console.log(data.Albanie.J1.nom);
        console.log(team1+" "+team2);
        $.each(data_team1,function(key,val){
            var $array_body = $('.tbody_eq1');
            var row = "<tr><td>"+val.num+"</td><td>"+val.nom+"</td><td>"+val.poste+"</td><td>"+val.age+"</td></tr>";
            $array_body.append(row);
        })

        $.each(data_team2,function(key,val){
            var $array_body = $('.tbody_eq2');
            var row = "<tr><td>"+val.num+"</td><td>"+val.nom+"</td><td>"+val.poste+"</td><td>"+val.age+"</td></tr>";
            $array_body.append(row);
        })

    });


    $('#top h1').text(data.header.eq1+" - "+data.header.eq2.replace(/~/g,' '));
    $('#top h3').text(moment(data.header.date).locale('en').format("dddd, MMMM Do YYYY") + " , "+moment(data.header.hour,'H').format('ha'));

    console.log("./img/flags/Flag of "+data.header.eq1.replace(/~/g,'-')+".png");

    $('#top #eq1').attr("src","./img/flags/Flag of "+data.header.eq1.replace(/~/g,'-')+".png");
    $('#top #eq2').attr("src","./img/flags/Flag of "+data.header.eq2.replace(/~/g,'-')+".png");

    $('#team1_lineup').attr("src","./img/flags/Flag of "+data.header.eq1.replace(/~/,'-')+".png");
    $('#team2_lineup').attr("src","./img/flags/Flag of "+data.header.eq2.replace(/~/,'-')+".png");
    $('.events').clone()
})

    //$('#top h1').text(data.header.eq1);

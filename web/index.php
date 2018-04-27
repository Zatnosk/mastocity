<?php

$r = empty($_GET['r']) ? 3 : intval($_GET['r']);
$x = empty($_GET['x']) ? 0 : intval($_GET['x']);
$y = empty($_GET['y']) ? 0 : intval($_GET['y']);
$r = max(2,min(7,$r));
$x_min = $x - $r;
$y_min = $y - $r;
$d = 2*$r+1;
$x_max = $x_min + $d;
$y_max = $y_min + $d;
$s = $d + 2;

function lot($x, $y, $people = null){
	$x++;
	$y++;
	$style = "style=\"grid-row:$y;grid-column:$x;\"";
	if(isset($people['owner'])) $people = array($people);
	if(isset($people)){
		$len = min(5,count($people));
		echo "\n\t\t<div class=lot $style><a href=\"#{$x}x$y\"><img src=\"img/house$len.png\"></a></div>";
		echo "\n\t\t<div class=inside id={$x}x$y><img class=icon src=\"img/house$len.png\"><a class=close href=\"#\">X</a>";
		foreach($people as $person){
			echo "<a class=button href=\"$person[url]\">$person[owner]</a>";
		}
		echo "</div>";
	} else {
		echo "\n\t\t<img src=\"img/empty.png\" $style>";
	}
}

require_once "config.php";
$mysqli = new Mysqli(Config::DBHOST, Config::DBUSER, Config::DBPASS, Config::DBNAME);
$sql = "SELECT *
        FROM houses
        WHERE x >= $x_min AND x <= $x_max
        	AND y >= $y_min AND y <= $y_max
        ORDER BY since ASC";
$query = $mysqli->query($sql);
$lots = array();
while($row = $query->fetch_assoc()){
	$i = $row['x'];
	$j = $row['y'];
	if(!isset($lots[$i])) $lots[$i] = array();
	if(!isset($lots[$i][$j])) $lots[$i][$j] = array();
	$lots[$i][$j][] = array('owner'=>$row['owner'],'url'=>$row['url']);
}
?>
<!DOCTYPE html>
<html>
<head>
	<title>Mastocity</title>
	<style type="text/css">
		:root {
			--light-green: #91d200;
			--dark-green: #415f00;
			--light-brown: #cca000;
		}
		body {
			font-family: sans-serif;
			background-color: black;
			color: white;
		}
		main {
			display: grid;
			width: <?=$s*90-10?>px;
			min-height: <?=($s)*90-10?>px;
			max-height: <?=($s+2)*90-10?>px;
			margin: 1rem auto;
			grid-template: repeat(<?=$s?>,80px) [bottom] / repeat(<?=$s?>,80px);
			grid-auto-rows: 170px;
			grid-gap: 10px;
			position: relative;
		}
		.button {
			margin: .5rem;
			padding: .5rem;
			z-index: 15;
			border-radius: 1rem;
			display: flex;
			text-align: center;
			align-items: center;
			justify-content: center;
			text-decoration: none;
			background-color: #415f00;
			border-width: 3px;
			border-color: #91d200;
			border-style: solid;
			color: #91d200;
		}
		.button:hover {
			background-color: #91d200;
			color: #415f00;
		}
		main > .buttom:hover {
			font-weight: 700;
		}
		.button.overview {
			grid-row: 1/2;
			grid-column: 1/3;
		}
		.button.up {
			grid-row: 1 / 2;
			grid-column: 3 / <?=$s-1?>;
		}
		.button.right {
			grid-row: 3 / <?=$s-1?>;
			grid-column: <?=$s?> / <?=$s+1?>;
		}
		.button.down {
			grid-row: <?=$s?> / <?=$s+1?>;
			grid-column: 3 / <?=$s-1?>;
		}
		.button.left {
			grid-row: 3 / <?=$s-1?>;
			grid-column: 1 / 2;
		}
		.button.narrow {
			grid-row: <?=$s?> / <?=$s+1?>;
			grid-column: 1 / 3;
		}
		.button.wide {
			grid-row: <?=$s?> / <?=$s+1?>;
			grid-column: <?=$s-1?> / <?=$s+1?>;
		}
		.grass {
			background-color: #415f00;
		}
		.lot {
			display: flex;
			flex-direction: column;
			width: 80px;
			height: 80px;
			position: relative;
			justify-content: center;
			align-items: center;
		}
		a {
			text-decoration: none;
			display: block;
		}
		.lot img {
			position: absolute;
			top: 0px;
			left: 0px;
			z-index: 10;
		}
		
		.inside {
			grid-row: bottom / span 1;
			grid-column: 1 / <?=$s+1?>;
			margin: calc(1rem);
			margin-top: .5rem;

			display: none;


			background-color: #cca000;
			z-index: 20;
			justify-content: center;
			align-items: start;
			flex-wrap: wrap;
			position: relative;
			border-radius: .5rem;
		}
		.inside::before {
			position: absolute;
			top: -.5rem;
			left: -.5rem;
			right: -.5rem;
			bottom: -.5rem;
			content: '';
			border-width: 3px;
			border-color: #91d200;
			border-style: solid;
			border-radius: 1rem;
			z-index: 5;
		}
		.inside * {
			z-index: 10;
		}
		.inside:target {
			display: flex;
		}
		.inside .icon {
			position: absolute;
			top: 0;
			left: 0;
			border-radius: .5rem 0;
			border-width: 0 3px 3px 0;
			border-color: #415f00;
			border-style: solid;
		}
		.inside .close {
			position: absolute;
			top: 0;
			right: 0;
			margin: 0;
			width: 1rem;
			height: 1rem;
			line-height: 1rem;
			border-radius: 0 .5rem;
			background-color: rgba(0,0,0,.5);
			color: #eee;
			text-align: center;
			padding: .5rem;
		}
		.inside .close:hover {
			background-color: rgba(0,0,0,.8);
		}

		.highlight {
			grid-row: <?=$r+2?>;
			grid-column: <?=$r+2?>;
			width: 84px;
			height: 84px;
			margin: -4px;
			border: 2px solid #91d200;
		}
		.debug {
			position: absolute;
			top: 1rem;
			left: 1rem;
		}
	</style>
</head>
<body>

<?
if(isset($_GET['debug'])){
	echo "<div class=debug>R,D,S: $r,$d,$s<br>X: $x_min ≤ $x < $x_max<br>Y: $y_min ≤ $y < $y_max</div>";
}
function href($dx,$dy,$dr = 0){
	global $x,$y,$r;
	$dx += $x;
	$dy += $y;
	$dr += $r;
	$href = array();
	if($dx != 0) $href[] = "x=$dx";
	if($dy != 0) $href[] = "y=$dy";
	if(isset($_GET['r']) || $dr != 0) $href[] = "r=$dr";
	if(isset($_GET['debug'])) $href[] = "debug";
	return '?'.implode('&',$href);
}
?>
	<main class=grass>
		<a href="overview.php" class="button overview">ZOOM OUT</a>
		<a href="<?=href(0,-1)?>" class="button up">MOVE UP</a>
		<a href="<?=href(1,0)?>" class="button right">MOVE RIGHT</a>
		<a id="movedown" href="<?=href(0,1)?>#movedown" class="button down">MOVE DOWN</a>
		<a href="<?=href(-1,0)?>" class="button left">MOVE LEFT</a>
		<?if($r>2){?><a href="<?=href(0,0,-1)?>" class="button narrow">NARROWER</a><?}?>
		<?if($r<7){?><a href="<?=href(0,0,1)?>" class="button wide">WIDER</a><?}?>
		<?php
			for($i=$x_min; $i<$x_max; $i++){
				for($j=$y_min; $j<$y_max; $j++){
					if(isset($lots[$i][$j])){
						lot($i-$x_min+1,$j-$y_min+1,$lots[$i][$j]);
					} else {
						lot($i-$x_min+1,$j-$y_min+1);
					}
				}
			}
		?>
		<div class=highlight></div>
	</main>
</body>
</html>
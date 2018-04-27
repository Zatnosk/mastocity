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
			width: 556px;
			height: 556px;
			margin: 1rem auto;
			grid-template: repeat(31,16px) / repeat(31,16px);
			grid-gap: 2px;
			position: relative;
			padding-bottom: 2rem;
		}
		.grass {
			background-color: #415f00;
		}
		.lot {
			display: block;
			width: 16px;
			height: 16px;
			color: rgba(0,0,0,.75);
			font-family: monospace;
			font-size: 12px;
			line-height: 16px;
			text-decoration: none;
			text-align: center;
			justify-content: center;
			align-items: center;
			background-color: #6a9900;
		}
		.lot.filled {
			background-color: #cca000;
		}
		.lot .owner {
			display: none;
			position: absolute;
			bottom: 0;
			left: 0;
			padding: .5rem;
			margin: 0;
			color: #91d200;
			font-size: 1rem;
		}
		.lot:hover .owner {
			display: block;
		}
	</style>
</head>
<?php
function lot($i, $j, $x=0, $y=0, $lot=null){
	echo "<a class=\"lot";
	if($lot){
		echo " filled";
	}
	echo "\" href=\"./?x=$x&y=$y&r=2\" style=\"grid-row:$j;grid-column:$i;\">";
	if($lot){
		echo $lot['owner'][1];
		echo "<p class=\"owner\">$lot[owner]</p>";
	}
	echo "</a>";
}
$x_offset = isset($_GET['x']) ? intval($_GET['x']) - 16 : -16;
$y_offset = isset($_GET['y']) ? intval($_GET['y']) - 16 : -16;
$x_max = $x_offset + 31;
$y_max = $y_offset + 31;

require_once "config.php";
$mysqli = new Mysqli(Config::DBHOST, Config::DBUSER, Config::DBPASS, Config::DBNAME);
$sql = "SELECT *
        FROM houses
        WHERE x >= $x_offset AND x <= $x_max
        	AND y >= $y_offset AND y <= $y_max";
$query = $mysqli->query($sql);
$lots = array();
while($row = $query->fetch_assoc()){
	$x = $row['x'];
	$y = $row['y'];
	if(!isset($lots[$x])) $lots[$x] = array();
	$lots[$x][$y] = array('owner'=>$row['owner'],'url'=>$row['url']);
}
?>
<body>
	<main class=grass>
		<?php
			for($i=1; $i<=31; $i++){
				$x = $i + $x_offset;
				for($j=1; $j<=31; $j++){
					$y = $j + $y_offset;
					if(isset($lots[$x][$y])){
						lot($i,$j,$x,$y,$lots[$x][$y]);
					} else {
						lot($i,$j,$x,$y);
					}
				}
			}
		?>
	</main>
</body>
</html>
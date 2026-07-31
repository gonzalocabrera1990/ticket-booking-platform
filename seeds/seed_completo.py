import random
from datetime import timedelta
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.utils.text import slugify
from shows.models import ShowPlace, Address, Sector, MapLayoutObject, Category, Event, Show, ShowSector

# Procedimiento para poblar la base de datos con la informacion necesaria para las prubas de la UI.

# INFRAESTRUCTURA SUMINISTRADA ANTERIORMENTE
ESTADIOS_DATA = [
    {
        "name": "Estadio José María Minella",
        "capacity": 42000,
        "viewbox": "0 0 1000 1000",
        "address": {"street": "Av. Mundial '78 y Olimpíadas", "city": "Mar del Plata", "state": "Buenos Aires", "zip_code": "B7600"},
        "sectors": [
            {"name": "Campo Frontal", "capacity": 8000, "geometry": {"type": "path", "d": "M703.5 505C700.457 559.271 693.413 583.853 668.349 614C621.818 629.332 585.394 632.393 509.5 632C441.378 631.773 405.42 628.976 349.651 614C324.522 582.688 315.868 558.735 310 505H703.5Z", "fill": "#1C7D88"}},
            {"name": "Campo Trasero", "capacity": 10000, "geometry": {"type": "path", "d": "M310 500C313.047 445.315 320.099 420.547 345.196 390.169C391.785 374.72 430.51 358.104 506.5 358.5C574.709 358.729 613.161 375.08 669 390.169C694.162 421.72 698.124 445.856 704 500H310Z", "fill": "#4D38AA"}},
            {"name": "Platea Central Destechada", "capacity": 9000, "geometry": {"type": "path", "d": "M292.5 238.5C461.882 162.772 555.906 164.867 722 243L672 383C538.258 335.878 466.814 335.918 346 383L292.5 238.5Z", "fill": "#B18484"}},
            {"name": "Platea Lateral Derecha", "capacity": 7300, "geometry": {"type": "path", "d": "M728.5 246C808.75 314.403 840.176 366.647 857 500C839.159 643.625 809.107 696.365 728.5 753L675.5 614C720.231 525.779 718.27 475.584 675.5 385L728.5 246Z", "fill": "#D82E2E"}},
            {"name": "Platea Lateral Izquierda", "capacity": 7300, "geometry": {"type": "path", "d": "M283.5 753C203.25 684.597 171.824 632.353 155 499C172.841 355.375 202.893 302.635 283.5 246L336.5 385C291.769 473.221 293.73 523.416 336.5 614L283.5 753Z", "fill": "#D82E2E"}}
        ],
        "layout_objects": [
            {"name": "ESCENARIO", "type": "STAGE", "geometry": {"type": "rect", "x": 422, "y": 635, "width": 174, "height": 59, "fill": "#222222", "font-size": 19, "text_x": 506.962, "text_y": 669.124}}
        ]
    },
    {
        "name": "Movistar Arena",
        "capacity": 15000,
        "viewbox": "0 0 1000 1000",
        "address": {"street": "Humboldt 450", "city": "CABA", "state": "Buenos Aires", "zip_code": "C1414"},
        "sectors": [
            {"name": "Platea Baja Centro", "capacity": 500, "geometry": {"type": "path", "d": "M629.5 263.5L596 358.25H397.5L357 263.5H629.5Z", "fill": "#29B92E"}},
            {"name": "Platea Alta Centro", "capacity": 600, "geometry": {"type": "path", "d": "M666.5 195L643.5 259H351.5L325 195H666.5Z", "fill": "#B331C7"}},
            {"name": "Platea Baja Codo Derecho", "capacity": 360, "geometry": {"type": "path", "d": "M714 347.5L624 387.5L601 369L643.5 270L714 347.5Z", "fill": "#29B92E"}},
            {"name": "Platea Alta Codo Derecho", "capacity": 500, "geometry": {"type": "path", "d": "M677.5 202.5L790 316L737.5 347L646.5 263.5L677.5 202.5Z", "fill": "#B331C7"}},
            {"name": "Platea Baja Codo Izquierdo", "capacity": 360, "geometry": {"type": "path", "d": "M345.5 268.5L394 365.5L370 393L269 345.5L345.5 268.5Z", "fill": "#29B92E"}},
            {"name": "Platea Alta Codo Izquierdo", "capacity": 500, "geometry": {"type": "path", "d": "M312.5 202.5L345.5 263.5L263.5 344.5L202.5 315L312.5 202.5Z", "fill": "#B331C7"}},
            {"name": "Platea Baja Lateral Derecha", "capacity": 1900, "geometry": {"type": "path", "d": "M630.95 398.5L723.5 357V715L630.95 750.5V398.5Z", "fill": "#29B92E"}},
            {"name": "Platea Alta Lateral Derecha", "capacity": 2100, "geometry": {"type": "path", "d": "M735 355.5L795.5 322.5V701L735 728.5V355.5Z", "fill": "#B331C7"}},
            {"name": "Platea Baja Lateral Izquierda", "capacity": 1900, "geometry": {"type": "path", "d": "M270.5 355.5L366.5 401V747.5L270.5 718.5V355.5Z", "fill": "#29B92E"}},
            {"name": "Platea Alta Lateral Izquierdo", "capacity": 2100, "geometry": {"type": "path", "d": "M197.5 323L257 350V729.5L197.5 699.5V323Z", "fill": "#B331C7"}},
            {"name": "Campo VIP", "capacity": 1000, "geometry": {"type": "rect", "x": 384, "y": 662, "width": 231, "height": 76, "fill": "#1a427d"}},
            {"name": "Campo General", "capacity": 2300, "geometry": {"type": "rect", "x": 384, "y": 491, "width": 231, "height": 165, "fill": "#2056A7"}},
            {"name": "Campo Trasero", "capacity": 700, "geometry": {"type": "rect", "x": 384, "y": 391, "width": 231, "height": 92, "fill": "#2056A7"}},
        ],
        "layout_objects": [
            {"name": "ESCENARIO", "type": "STAGE", "geometry": {"type": "rect", "x": 415, "y": 753, "width": 169, "height": 56, "fill": "#222222", "font-size": 19, "text_x": 496.900, "text_y": 787.346}}
        ]
    },
    {
        "name": "Estadio Luna Park",
        "capacity": 9000,
        "viewbox": "0 0 1000 1000",
        "address": {"street": "Av. Eduardo Madero 420", "city": "CABA", "state": "Buenos Aires", "zip_code": "C1106"},
        "sectors": [
            {"name": "Campo", "capacity": 3400, "geometry": {"type": "path", "d": "M249 414H771V608H249V414Z", "fill": "#50DF43"}},
            {"name": "Platea Lateral Madero", "capacity": 900, "geometry": {"type": "path", "d": "M789.5 480.5H923V622.5H789.5V480.5Z", "fill": "#3D41FF"}},
            {"name": "Platea Pullman Este", "capacity": 1180, "geometry": {"type": "path", "d": "M876.5 291L921.54 337.5V471.5H788V418.5L763.5 397H677.5V291H876.5Z", "fill": "#1417D2"}},
            {"name": "Super Pullman", "capacity": 1500, "geometry": {"type": "path", "d": "M347.5 280H671V397H347.5V280Z", "fill": "#400C99"}},
            {"name": "Platea Pullman Oeste", "capacity": 1180, "geometry": {"type": "path", "d": "M95 340.5L154.5 291H341V397H254L227 422V469.5H95V340.5Z", "fill": "#1417D2"}},
            {"name": "Platea Lateral Corrientes", "capacity": 900, "geometry": {"type": "rect", "x": 95, "y": 481, "width": 132, "height": 142, "fill": "#3D41FF"}},
            {"name": "Sector Discapacitados", "capacity": 150, "geometry": {"type": "rect", "x": 702, "y": 614, "width": 69, "height": 23, "fill": "#400C99"}}
        ],
        "layout_objects": [
            {"name": "ESCENARIO", "type": "STAGE", "geometry": {"type": "path", "d": "M382.5 637H629.5V706H382.5V637Z", "fill": "#222222", "text_x": 502.9, "text_y": 679.85, "font-size": 25}}
        ]
    },
    {
        "name": "Estadio Mâs Monumental River Plate",
        "capacity": 84567,
        "viewbox": "0 0 1016 872",
        "address": {"street": "Av. Pres. Figueroa Alcorta 7597", "city": "CABA", "state": "Buenos Aires", "zip_code": "C1428"},
        "sectors": [
            {"name": "Sívori Alta", "capacity": 7000, "geometry": {"type": "path", "d": "M332.5 359.5C273.804 480.754 273.948 552.19 334.5 694L284.5 719.5C221.285 575.715 220 486 292 329.5L332.5 359.5Z", "fill": "#D50700"}},
            {"name": "San Martín Alta", "capacity": 5000, "geometry": {"type": "path", "d": "M718 321L670.5 349C549.66 225.518 459.294 229.941 336.5 348L296.5 321C425.682 156.882 582.995 157.935 718 321Z", "fill": "#D50700"}},
            {"name": "Centenario Alta", "capacity": 7000, "geometry": {"type": "path", "d": "M721.5 330.5C787.139 483.218 783.897 569.766 719 720.5L675 691.5C727.697 564.19 729.369 491.779 675 360.5L721.5 330.5Z", "fill": "#D50700"}},
            {"name": "Sívori Media", "capacity": 4000, "geometry": {"type": "path", "d": "M370 383.5C320.496 495.462 323.55 558.917 370 673L336.42 693C280.772 563.681 277.724 489.199 336.42 362L370 383.5Z", "fill": "#7B708C"}},
            {"name": "San Martín Media", "capacity": 3500, "geometry": {"type": "path", "d": "M666.5 351.951L632.5 375C552.535 280.185 464.391 280.162 375.5 373.039L340 349.009C460.102 230.707 551.216 227.231 666.5 351.951Z", "fill": "#7B708C"}},
            {"name": "Sívori Baja (Popular)", "capacity": 6000, "geometry": {"type": "path", "d": "M417 416V645.5L373 670.5C326.351 559.591 325.046 497.41 373 386.5L417 416V645.5Z", "fill": "#FF0505"}},
            {"name": "Belgrano Baja", "capacity": 3000, "geometry": {"type": "path", "d": "M630 377L590 405H419.5L377.5 376C469.713 279.486 548.514 284.168 630 377Z", "fill": "#FF0909"}},
            {"name": "Centenario Media", "capacity": 4000, "geometry": {"type": "path", "d": "M637.679 382.5L672.32 362C726.363 499.927 724.694 571.073 672.32 690L637.679 669.5C687.347 555.381 687.64 492.522 637.679 382.5Z", "fill": "#7B708C"}},
            {"name": "Centenario Baja", "capacity": 10000, "geometry": {"type": "path", "d": "M593.5 413L635 385C683.124 491.961 683.678 553.778 635 667.5L593.5 642.5V413Z", "fill": "#FF0909"}},
            {"name": "Campo Trasero", "capacity": 18000, "geometry": {"type": "rect", "x": 421, "y": 410, "width": 169, "height": 92, "fill": "#222222"}},
            {"name": "Campo VIP", "capacity": 12000, "geometry": {"type": "rect", "x": 421, "y": 508, "width": 169, "height": 89, "fill": "#7B708C"}}
        ],
        "layout_objects": [
             {"name": "ESCENARIO", "type": "STAGE", "geometry": {"type": "rect", "x": 426, "y": 604, "width": 159, "height": 35, "fill": "#000000", "text_x": 504.756, "text_y": 625.144, "font-size": 15 }}
        ]
    },
    {
        "name": "Campo Argentino de Polo",
        "capacity": 45000,
        "viewbox": "0 0 1000 1000",
        "address": {"street": "Intersección de Avenida del Libertado y Dorrego", "city": "Buenos Aires, Palermo", "state": "Buenos Aires", "zip_code": "B7600"},
        "sectors": [
            {"name": "VIP Oro Izquierdo", "capacity": 900, "geometry": {"x": 143, "y": 594, "fill": "#D59F28", "type": "rect", "width": 255, "height": 36}},
            {"name": "VIP Oro Derecho", "capacity": 1000, "geometry": {"x": 601, "y": 594, "fill": "#D59F28", "type": "rect", "width": 256, "height": 36}},
            {"name": "VIP Derecho", "capacity": 10000, "geometry": {"x": 537, "y": 528, "fill": "#FFD3A1", "type": "rect", "width": 320, "height": 55}},
            {"name": "VIP Izquierdo", "capacity": 7300, "geometry": {"x": 142, "y": 526, "fill": "#FFD3A1", "type": "rect", "width": 320, "height": 55}},

            {"name": "Campo de Pie", "capacity": 7300, "geometry": {"x": 143, "y": 352, "fill": "#D3D3D3", "type": "rect", "width": 714, "height": 165}},
            {"name": "Platea A", "capacity": 900, "geometry": {"x": 142, "y": 255, "fill": "#76EAFF", "type": "rect", "width": 215, "height": 75}},
            {"name": "Platea B", "capacity": 9000, "geometry": {"x": 374, "y": 255, "fill": "#76EAFF", "type": "rect", "width": 252, "height": 75}},
            {"name": "Platea C", "capacity": 900, "geometry": {"x": 642, "y": 255, "fill": "#76EAFF", "type": "rect", "width": 215, "height": 75}},

            {"name": "Platea Preferencial Derecha", "capacity": 7300, "geometry": {"x": 882, "y": 352, "fill": "#356BCF", "type": "rect", "width": 89, "height": 352}},
            {"name": "Platea Preferencial Izquierda", "capacity": 7300, "geometry": {"x": 28, "y": 352, "fill": "#356BCF", "type": "rect", "width": 89, "height": 352}},

            {"name": "VIP Platino", "capacity": 8000, "geometry": {"d": "M592.105 594.691L591.925 642.691L857.423 643.692L856.995 757.191L537.497 755.987L537.686 705.987L463.186 705.707L462.998 755.706L142 754.496L142.43 640.497L409.428 641.503L408.607 594L592.105 594.691Z", "fill": "#AC8123", "type": "path"}}
        ],
        "layout_objects": [
            {"name": "ESCENARIO", "type": "STAGE", "geometry": {"d": "M501 836L279 836V776.5L472 776.5L472 710H527.5V776.5L720.5 776.5V836L501 836Z", "fill": "#222222", "type": "path", "text_x": 500.01, "text_y": 810.901, "font-size": 19}},
            {"name": "Torre de Sonido", "type": "INFRA", "geometry": {"x": 472, "y": 526, "fill": "#787878", "type": "rect", "width": 54, "height": 54}}
        ]
    },
    {
        "name": "Teatro Gran Rex",
        "capacity": 3600,
        "viewbox": "0 0 1000 1000",
        "address": {"street": "Av. Corrientes 857", "city": "Cdad. Autónoma de Buenos Aires", "state": "Buenos Aires", "zip_code": "B7600"},
        "sectors": [
            {"name": "Platea Platino Centro", "capacity": 900, "geometry": {"type": "rect", "x": 398, "y": 771, "width": 177, "height": 105, "fill": "#F9BA72"}},
            {"name": "Platea Platino Izquierda", "capacity": 8000, "geometry": {"type": "path", "d": "M362.856 769.5V876L342.5 884L330.5 872V777.5L362.856 769.5Z", "fill": "#F9BA72"}},
            {"name": "Platea Platino Derecha", "capacity": 8000, "geometry": {"type": "path", "d": "M642.856 778.5V871L633 882L611 876.5V772L642.856 778.5Z", "fill": "#F9BA72"}},

            {"name": "Platea Oro Centro", "capacity": 900, "geometry": {"type": "rect", "x": 398, "y": 706, "width": 177, "height": 60, "fill": "#FFF481"}},
            {"name": "Platea Oro Izquierda", "capacity": 8000, "geometry": {"type": "path", "d": "M329.5 712.5L363.5 704V766L329.5 774.5V712.5Z", "fill": "#FFF481"}},
            {"name": "Platea Oro Derecha", "capacity": 8000, "geometry": {"type": "path", "d": "M643 710V774L611 766.5V704.5L643 710Z", "fill": "#FFF481"}},

            {"name": "Platea Plata Centro", "capacity": 900, "geometry": {"type": "rect", "x": 398, "y": 649, "width": 177, "height": 52, "fill": "#D3810E"}},
            {"name": "Platea Plata Izquierda", "capacity": 8000, "geometry": {"type": "path", "d": "M363 648.5V700.5L327 708.5V840L311.5 844V819.5L294.5 825L294 801.5L276.5 806V783L258.5 787.5L258 765.5L240.5 768V673.5L363 648.5Z", "fill": "#D3810E"}},
            {"name": "Platea Plata Derecha", "capacity": 8000, "geometry": {"type": "path", "d": "M610.5 649L770 680V776L743.5 770V783L733.5 777.5V790L716 786V809L698 805V827.5L680.5 825V846L647.5 839.5L646.5 707L611.5 700L610.5 649Z", "fill": "#D3810E"}},

            {"name": "Platea Bronce Centro", "capacity": 8000, "geometry": {"type": "path", "d": "M363.5 604V645L204 676V647.5H211.5V634.5L363.5 604Z", "fill": "#F1D001"}},
            {"name": "Platea Bronce Izquierda", "capacity": 8000, "geometry": {"type": "path", "d": "M431.5 584H574.5V645.5L399 645L398 573.5H431.5V584Z", "fill": "#F1D001"}},
            {"name": "Platea Bronce Derecha", "capacity": 8000, "geometry": {"type": "path", "d": "M610.5 572L765 597V611.5H778.5V624H788V636H798.5L796.5 668H805.5V682.5L610.5 645V572Z", "fill": "#F1D001"}},

            {"name": "Platea Bronce Lateral Izquierda", "capacity": 8000, "geometry": {"type": "path", "d": "M204.077 680.5L237 674V774L255.5 769V793.5L273 786.5V811L291 805L292 830.5L309.5 824.5L308 848.5L326.5 842.5V874H320L317 864.5L306 867L293.5 852V845L279.5 852L212.5 782V763L204.077 765.25V680.5Z", "fill": "#C32722"}},
            {"name": "Platea Bronce Lateral Derecha", "capacity": 8000, "geometry": {"type": "path", "d": "M773 681L805.5 687.5V750L797 746.5V769L789 767.5V779L780 776.5V788.5L770.5 786.5L771.5 794.5L733 835.5L716 830.5V843.5L701.5 839.5L691.5 860.5L672 855V867.5L653.5 863.5L655 873L646.5 876.5L647 843.5L683.5 849.5V828.5L701.5 830.5L700 810.5L720.5 814L719 792L736.5 796.5V782.5L745.5 788.5V775L773 780.048V681Z", "fill": "#C32722"}},

            {"name": "Super Poolman Bajo Izquierdo", "capacity": 8000, "geometry": {"type": "path", "d": "M175.5 504.5L341.5 469.5V521.5L157 559.5L155 528L175.5 504.5Z", "fill": "#E9CADE"}},
            {"name": "Super Poolman Bajo Centro", "capacity": 8000, "geometry": {"type": "path", "d": "M375.5 473H599.5V491H593.5V523.5H382V492.5H375.5V473Z", "fill": "#E9CADE"}},
            {"name": "Super Poolman Bajo Derecho", "capacity": 8000, "geometry": {"type": "path", "d": "M632 471.5L818.5 507V538.5L828.5 541L827.5 560.5L632 523.5V471.5Z", "fill": "#E9CADE"}},

            {"name": "Super Poolman Alto Izquierdo", "capacity": 8000, "geometry": {"type": "path", "d": "M632 415.5L773 442.5V460L783 462.5V476.5L802 480V491L813 493.5V502.5L632 466.5V415.5Z", "fill": "#D07FAE"}},
            {"name": "Super Poolman Alto Centro", "capacity": 8000, "geometry": {"type": "path", "d": "M484 439.5H501.5V428H544.5V439.5H573V428H598.5V468H375.5V439.5H401V450.5H420.5V439.5H473V450.5H484V439.5Z", "fill": "#D07FAE"}},
            {"name": "Super Poolman Alto Derecho", "capacity": 8000, "geometry": {"type": "path", "d": "M199 475L306.5 454L306 463L340.5 455.5V466.5L179 499V488.5L199 485V475Z", "fill": "#D07FAE"}},

            {"name": "Poolman Bajo Izquierdo", "capacity": 8000, "geometry": {"type": "path", "d": "M255.5 296.5V370L103.5 401V393.5L113 390V346.5L122 343.5V323.5L255.5 296.5Z", "fill": "#DCE49E"}},
            {"name": "Poolman Bajo Derecho", "capacity": 8000, "geometry": {"type": "path", "d": "M717 297.5L868.5 327.5V336.5L885 340V383.5L895.5 386.5V397L885 395V404L717 370V297.5Z", "fill": "#DCE49E"}},
            {"name": "Poolman Bajo Centro", "capacity": 8000, "geometry": {"type": "path", "d": "M570.5 297V314.5L565 323.5V368.5H425V323.5L420 314.5V297H570.5Z", "fill": "#DCE49E"}},
            {"name": "Poolman Bajo Centro", "capacity": 900, "geometry": {"type": "rect", "x": 316, "y": 362, "width": 44, "height": 9, "fill": "#DCE49E"}},
            {"name": "Poolman Bajo Centro", "capacity": 900, "geometry": {"type": "rect", "x": 630, "y": 362, "width": 44, "height": 9, "fill": "#DCE49E"}},
            {"name": "Poolman Bajo Centro", "capacity": 900, "geometry": {"type": "rect", "x": 630, "y": 295, "width": 44, "height": 9, "fill": "#DCE49E"}},
            {"name": "Poolman Bajo Centro", "capacity": 900, "geometry": {"type": "rect", "x": 316, "y": 295, "width": 44, "height": 9, "fill": "#DCE49E"}},

            {"name": "Poolman Medio A Izquierdo", "capacity": 8000, "geometry": {"type": "path", "d": "M122 257.5L255 230V293.5L122 320.5V311.5L131 309V286.5L122 288V257.5Z", "fill": "#8DB235"}},
            {"name": "Poolman Medio A Derecho", "capacity": 8000, "geometry": {"type": "path", "d": "M716.5 230.5L841 255V265.5L859 269V289L868.5 292V314.5L859 312V321.5L716.5 293.5V230.5Z", "fill": "#8DB235"}},
            {"name": "Poolman Medio A Centro", "capacity": 8000, "geometry": {"type": "path", "d": "M585 229.5L577.022 293H415.468L404 229.5H585Z", "fill": "#8DB235"}},
            {"name": "Poolman Medio A Centro", "capacity": 900, "geometry": {"type": "rect", "x": 316, "y": 274, "width": 44, "height": 19, "fill": "#8DB235"}},
            {"name": "Poolman Medio A Centro", "capacity": 900, "geometry": {"type": "rect", "x": 630, "y": 274, "width": 44, "height": 19, "fill": "#8DB235"}},

            {"name": "Poolman Medio B Izquierdo", "capacity": 8000, "geometry": {"type": "path", "d": "M130.5 189.5L254.5 164V226.5L122 253V244.5L137.5 240.5V220.5L130.5 222V189.5Z", "fill": "#CAE4F6"}},
            {"name": "Poolman Medio B Derecho", "capacity": 8000, "geometry": {"type": "path", "d": "M716.5 163L833 187.5V197L841 199V251.5L716.5 227.25V163Z", "fill": "#CAE4F6"}},
            {"name": "Poolman Medio B Centro", "capacity": 8000, "geometry": {"type": "path", "d": "M599.5 165L585.5 226H402L391 165H599.5", "fill": "#CAE4F6"}},
            {"name": "Poolman Medio B Centro", "capacity": 900, "geometry": {"type": "rect", "x": 312, "y": 164, "width": 44, "height": 52, "fill": "#CAE4F6"}},
            {"name": "Poolman Medio B Centro", "capacity": 900, "geometry": {"type": "rect", "x": 626, "y": 164, "width": 44, "height": 52, "fill": "#CAE4F6"}},

            {"name": "Poolman Alto A Izquierdo", "capacity": 8000, "geometry": {"type": "path", "d": "M139.5 154V140.5L130 142.5V134L255 108.5V161L130 185.5V156.5L139.5 154Z", "fill": "#5D9CD3"}},
            {"name": "Poolman Alto A Derecho", "capacity": 8000, "geometry": {"type": "path", "d": "M814.5 128V160.5L824 162.5V182L716 160.5V108.5L814.5 128Z", "fill": "#5D9CD3"}},
            {"name": "Poolman Alto A Centro", "capacity": 8000, "geometry": {"type": "path", "d": "M571 109.5H607.5V138.5L601 142.5V161.5H389.5L388 142.5L383 138.5V109.5H411V131.5H571V109.5Z", "fill": "#5D9CD3"}},
            {"name": "Poolman Alto A Centro", "capacity": 900, "geometry": {"type": "rect", "x": 312, "y": 109, "width": 44, "height": 52, "fill": "#5D9CD3"}},
            {"name": "Poolman Alto A Centro", "capacity": 900, "geometry": {"type": "rect", "x": 626, "y": 109, "width": 44, "height": 52, "fill": "#5D9CD3"}},

            {"name": "Poolman Alto B Izquierdo", "capacity": 8000, "geometry": {"type": "path", "d": "M130 122L255 97V106L130 131V122Z", "fill": "#265374"}},
            {"name": "Poolman Alto B Centro", "capacity": 900, "geometry": {"type": "rect", "x": 285, "y": 98, "width": 125, "height": 9, "fill": "#265374"}},
            {"name": "Poolman Alto B Centro", "capacity": 900, "geometry": {"type": "rect", "x": 572, "y": 98, "width": 117, "height": 9, "fill": "#265374"}},
            {"name": "Poolman Alto B Derecho", "capacity": 8000, "geometry": {"type": "path", "d": "M716 97L814.5 116.5V125.5L716 105.5V97Z", "fill": "#265374"}},

        ],
        "layout_objects": [
            {"name": "ESCENARIO", "type": "STAGE", "geometry": {"type": "rect", "x": 388, "y": 910, "width": 199, "height": 32, "fill": "#222222", "text_x": 487.009, "text_y": 934.186, "font-size": 12}}
        ]
    }
]

# NUEVO POOL COMPLETADO Y SELECCIONADO POR EL USUARIO
CATEGORIAS_DATA = [
    {"name": "Rock", "icon": "bi-music-note-beamed", "color": "#dc3545"},
    {"name": "Pop", "icon": "bi-stars", "color": "#e83e8c"},
    {"name": "Trap & Hip-Hop", "icon": "bi-lightning-fill", "color": "#6f42c1"},
    {"name": "Heavy Metal", "icon": "bi-activity", "color": "#343a40"},
    {"name": "Electrónica", "icon": "bi-disc-fill", "color": "#007bff"},
    {"name": "Teatro", "icon": "bi-ticket-perforated-fill", "color": "#b50404"},
]

SHOWS_POOL = [
    {"title": "Duki - Americana Tour", "cat": "Trap & Hip-Hop", "desc": "El referente definitivo del trap argentino.", "dias": 15, "intl": False},
    {"title": "Wos - Descartable", "cat": "Rock", "desc": "Presentación oficial de su nuevo álbum con banda en vivo.", "dias": 20, "intl": False},
    {"title": "Babasónicos en Concierto", "cat": "Rock", "desc": "La banda más elegante del rock nacional repasa su discografía.", "dias": 25, "intl": False},
    {"title": "La Renga - Totalmente Poseídos", "cat": "Rock", "desc": "El banquete más esperado del año. Puro rock barrial.", "dias": 30, "intl": False},
    {"title": "Divididos - 35 Años", "cat": "Rock", "desc": "La aplanadora del rock celebra su trayectoria con un show demoledor.", "dias": 35, "intl": False},
    {"title": "Fito Páez - El Amor Después del Amor", "cat": "Rock", "desc": "El concierto histórico que celebra el disco más vendido de la historia nacional.", "dias": 40, "intl": False},
    {"title": "Airbag - Jinetes Cromados", "cat": "Rock", "desc": "Los hermanos Sardelli desatan su potencia eléctrica de guitarras.", "dias": 45, "intl": False},
    {"title": "Los Fabulosos Cadillacs", "cat": "Rock", "desc": "El regreso de una leyenda de los ritmos latinos, el ska y el rock.", "dias": 50, "intl": False},
    {"title": "Ciro y los Persas - Ritual 2026", "cat": "Rock", "desc": "Andrés Ciro Martínez revive los clásicos de Los Piojos.", "dias": 55, "intl": False},
    {"title": "Miranda! - Hotel Miranda VIP", "cat": "Pop", "desc": "El dúo pop más icónico de Latinoamérica transforma el estadio en una fiesta.", "dias": 60, "intl": False},
    {"title": "Nicki Nicole - Alma Tour", "cat": "Trap & Hip-Hop", "desc": "La artista rosarina despliega su talento y sensibilidad urbana.", "dias": 65, "intl": False},
    {"title": "Las Pastillas del Abuelo", "cat": "Rock", "desc": "Una velada de rock fusión y letras profundas barriales.", "dias": 70, "intl": False},
    {"title": "Cuarteto de Nos - Lámina Once", "cat": "Rock", "desc": "Los uruguayos regresan con sus letras filosas e ingeniosas.", "dias": 75, "intl": False},
    {"title": "El Kuelgue - Hola Precioso", "cat": "Pop", "desc": "Improvisación, absurdo y un despliegue musical exquisito.", "dias": 80, "intl": False},
    {"title": "Conociendo Rusia - Jet Love", "cat": "Rock", "desc": "El proyecto liderado por Mateo Sujatovich con su pop-rock clásico.", "dias": 85, "intl": False},
    {"title": "Coldplay - Music of the Spheres II", "cat": "Pop", "desc": "El regreso del fenómeno global con su despliegue de pulseras LED.", "dias": 90, "intl": True},
    {"title": "Metallica - M72 World Tour", "cat": "Heavy Metal", "desc": "Los gigantes del thrash metal llegan con su imponente escenario central 360.", "dias": 95, "intl": True},
    {"title": "The Weeknd - After Hours til Dawn", "cat": "Pop", "desc": "Un viaje conceptual a través del synth-pop y R&B espacial.", "dias": 100, "intl": True},
    {"title": "Arctic Monkeys - AM Tour", "cat": "Rock", "desc": "Alex Turner y compañía traen el rock alternativo de Sheffield con pura elegancia.", "dias": 105, "intl": True},
    {"title": "Green Day - The Saviors Tour", "cat": "Rock", "desc": "La banda ícono del punk rock celebra los aniversarios de Dookie.", "dias": 110, "intl": True},
    {"title": "Dua Lipa - Radical Optimism", "cat": "Pop", "desc": "La reina del pop británico llega para encender la pista con sus hits mundiales.", "dias": 115, "intl": True},
    {"title": "Iron Maiden - Run For Your Lives", "cat": "Heavy Metal", "desc": "La leyenda del heavy metal celebra 50 años de trayectoria junto a Eddie.", "dias": 120, "intl": True},
    {"title": "Bruno Mars - Live in Concert", "cat": "Pop", "desc": "El showman definitivo del funk y el pop despliega su carisma bailable.", "dias": 125, "intl": True},
    {"title": "Radiohead - Sonic Experience", "cat": "Rock", "desc": "Una experiencia sónica e introspectiva única de la mano de Thom Yorke.", "dias": 130, "intl": True},
    {"title": "Travis Scott - Utopia", "cat": "Trap & Hip-Hop", "desc": "El máximo exponente del trap mundial promete desatar los pogos más salvajes.", "dias": 135, "intl": True},
    {"title": "Foo Fighters - Electric Tour", "cat": "Rock", "desc": "Dave Grohl lidera la celebración eterna del rock de guitarras enérgico.", "dias": 140, "intl": True},
    {"title": "Depeche Mode - Memento Mori", "cat": "Electrónica", "desc": "Los pioneros del synth-rock regresan en una noche nostálgica y electrónica.", "dias": 145, "intl": True},
    {"title": "Pearl Jam - Dark Matter", "cat": "Rock", "desc": "Eddie Vedder y los suyos traen el espíritu intacto del grunge de Seattle.", "dias": 150, "intl": True},
    {"title": "Gorillaz - Cracker Island Live", "cat": "Pop", "desc": "Damon Albarn fusiona visuales animadas en pantallas con hip-hop y dub.", "dias": 155, "intl": True},
    {"title": "Eric Clapton", "cat": "Rock", "desc": "El espíritu intacto del rock del británico, en un show enérgico y cambiante.", "dias": 150, "intl": True},
    {"title": "Mark Knopfler", "cat": "Rock", "desc": "El regreso del escocés en una noche nostálgica y de alto impacto.", "dias": 145, "intl": True},
    {"title": "OASIS", "cat": "Rock", "desc": "El regreso del fenómeno global del rock and roll. Durante su gira mundial, Argentina los recibe para dos noches a pura nostalgia y rock.", "dias": 90, "intl": True},
    {"title": "INVASIONES I", "cat": "Teatro", "desc": "El espectáculo que cuenta con más de treinta artistas en escena propone una mirada contemporánea sobre un episodio fundacional de la historia argentina: las invasiones inglesas de 1806. A partir de una ambiciosa puesta en escena con gran despliegue, la obra busca reflejar los momentos de desconcierto y resistencia que precedieron a la defensa del Río de la Plata, acompañada por una banda sonora inspirada en el universo musical de Charly García.", "dias": 90, "intl": True}
]

class Command(BaseCommand):
    help = 'Repobla la BD masivamente con 31 eventos asignados de forma inteligente por estadios y categorías.'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.WARNING('=== Vaciando tablas comerciales e infraestructuras ==='))
        ShowSector.objects.all().delete()
        Show.objects.all().delete()
        Event.objects.all().delete()
        Category.objects.all().delete()
        MapLayoutObject.objects.all().delete()
        Sector.objects.all().delete()
        Address.objects.all().delete()
        ShowPlace.objects.all().delete()
        self.stdout.write(self.style.SUCCESS('Base de datos limpia de raíz.'))

        # -------------------------------------------------------------
        # 1. CARGA AUTOMATIZADA DE INFRAESTRUCTURA SVG REAL
        # -------------------------------------------------------------
        self.stdout.write(self.style.WARNING('=== Indexando los 4 Estadios Reales y Polígonos SVG ==='))
        dict_estadios = {}

        for est_info in ESTADIOS_DATA:
            lugar = ShowPlace.objects.create(
                name=est_info["name"],
                capacity=est_info["capacity"],
                viewbox=est_info["viewbox"]
            )
            dict_estadios[est_info["name"]] = lugar

            adr = est_info["address"]
            Address.objects.create(
                place=lugar, street=adr["street"], city=adr["city"], 
                state=adr["state"], zip_code=adr["zip_code"]
            )

            for sec_info in est_info["sectors"]:
                Sector.objects.create(
                    place=lugar,
                    name=sec_info["name"],
                    slug=slugify(sec_info["name"]),
                    capacity=sec_info["capacity"],
                    polygon_geometry=sec_info["geometry"]
                )

            for lay_info in est_info["layout_objects"]:
                MapLayoutObject.objects.create(
                    place=lugar, name=lay_info["name"], object_type=lay_info["type"],
                    geometry=lay_info["geometry"]
                )
        
        self.stdout.write(self.style.SUCCESS('Estadios e Infraestructuras guardados con éxito.'))

        # -------------------------------------------------------------
        # 2. CARGA DE CATEGORÍAS
        # -------------------------------------------------------------
        dict_categorias = {}
        for cat_info in CATEGORIAS_DATA:
            categoria = Category.objects.create(
                name=cat_info["name"],
                slug=slugify(cat_info["name"]),
                color_hex=cat_info["color"],
                icon_class=cat_info["icon"]
            )
            dict_categorias[cat_info["name"]] = categoria

        # -------------------------------------------------------------
        # 3. CONFECCIÓN E INSERCIÓN DE EVENTOS Y FUNCIONES MASIVAS
        # -------------------------------------------------------------
        self.stdout.write(self.style.WARNING('=== Generando la Cartelera de 31 Artistas y sus Funciones ==='))
        ahora = timezone.now()

        # Instancias de estadios para asignación lógica
        river = dict_estadios["Estadio Mâs Monumental River Plate"]
        movistar = dict_estadios["Movistar Arena"]
        luna_park = dict_estadios["Estadio Luna Park"]
        minella = dict_estadios["Estadio José María Minella"]

        for item in SHOWS_POOL:
            # Creamos el evento de marketing estático
            evento = Event.objects.create(
                title=item["title"],
                description=item["desc"],
                category=dict_categorias.get(item["cat"]),
                image_url=f"https://images.unsplash.com/photo-1514525253161-7a46d19cd819?w=400&q=80"
            )

            # LÓGICA DE ASIGNACIÓN INTERMEDIA DE ESTADIO
            # Si es internacional de Pop/Metal va a River. Si es Trap/Electrónica nacional va al Movistar o Luna.
            if item["intl"] and item["cat"] in ["Pop", "Heavy Metal", "Rock"]:
                estadio_destino = river
                cant_funciones = random.choice([2, 3]) # Simulamos múltiples noches (giras de estadios)
            elif item["cat"] in ["Trap & Hip-Hop", "Electrónica", "Pop"]:
                estadio_destino = random.choice([movistar, luna_park])
                cant_funciones = random.choice([1, 2])
            else:
                estadio_destino = random.choice([minella, luna_park])
                cant_funciones = 1

            # Creamos las funciones comerciales calculando las fechas hacia el futuro
            for f_idx in range(1, cant_funciones + 1):
                # Desfasamos las noches consecutivas sumando días adicionales
                fecha_funcion = ahora + timedelta(days=item["dias"] + (f_idx - 1))
                
                # Seteamos un precio base sugerido comercial inteligente
                precio_base_mkt = 50000.00 if item["intl"] else 25000.00

                show = Show.objects.create(
                    event=evento,
                    place=estadio_destino,
                    date=fecha_funcion,
                    price=precio_base_mkt
                )

                # Generamos el inventario real para cada sector de ese estadio en esa noche específica
                for sector in estadio_destino.sectors.all():
                    # Calculamos tarifas coherentes basadas en las palabras del sector
                    if "VIP" in sector.name or "Frontal" in sector.name or "Centro" in sector.name:
                        tarifa = precio_base_mkt * 2
                    elif "Alta" in sector.name or "Trasero" in sector.name:
                        tarifa = precio_base_mkt * 0.7
                    else:
                        tarifa = precio_base_mkt * 1.2

                    # Recargo opcional si es la última noche por alta demanda
                    if f_idx > 1:
                        tarifa += 5000.00

                    # Simulamos ventas y reservas proporcionales al tamaño del sector
                    porcentaje_ocupacion = random.uniform(0.15, 0.85)
                    vendidas = int(sector.capacity * porcentaje_ocupacion)
                    reservadas = random.randint(10, min(100, sector.capacity - vendidas))

                    # ShowSector.objects.create(
                    #     show=show,
                    #     sector=sector,
                    #     price=tarifa,
                    #     sold=vendidas,
                    #     reserved=reservadas
                    # )
                    ShowSector.objects.create(
                        show=show,
                        sector=sector,
                        price=tarifa,
                        sold=0,
                        reserved=0
                    )

        self.stdout.write(self.style.SUCCESS(f'=== ¡Éxito total! Se cargaron los 31 Eventos con sus respectivos ShowSectors en cascada V3. ==='))

# Instanciamos la clase y llamamos al método handle manualmente
cmd = Command()
cmd.handle()
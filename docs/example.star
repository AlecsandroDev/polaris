STAR Sun {
    MASS 1 solar_mass;
    TEMPERATURE 5778 K;
    TYPE G2V;
};


PLANET Earth {
    MASS 1 earth_mass;
    RADIUS 1 earth_radius;

    ORBIT Sun {
        DISTANCE 1 AU;
        PERIOD 365.25 day;
    };
};

OBSERVE orbita_sol_terra {
    FROM Earth;
    TO Sun;
    DISTANCE;
    VELOCITY;
};

PRINT_S(orbita_sol_terra); # Print na tela

READ_S(); # Leitura Terminal

IF_S (orbita_sol_terra < 1.5 AU) {
    PRINT_S("PERTO"); 
} 
ELSE {
    PRINT_S("LONGE"); 
};

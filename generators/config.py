N_PATIENTS = 1000
N_GPS = 75
N_INSURANCES = 8
RANDOM_SEED = 42

SOURCE_SYSTEMS = ("EPD_A", "EPD_B", "EPD_C")

# Share of records by source when assigning single-source memberships.
SOURCE_VOLUME_WEIGHTS = {
	"EPD_A": 0.52,
	"EPD_B": 0.33,
	"EPD_C": 0.15,
}

# Distribution for how many systems a real person appears in.
SOURCE_OVERLAP_DISTRIBUTION = {
	1: 0.76,
	2: 0.20,
	3: 0.04,
}

# Pair frequencies for patients present in exactly two systems.
SOURCE_PAIR_WEIGHTS = {
	("EPD_A", "EPD_B"): 0.50,
	("EPD_A", "EPD_C"): 0.30,
	("EPD_B", "EPD_C"): 0.20,
}

SOURCE_NOISE_PROFILES = {
	"EPD_A": {
		"name_noise_rate": 0.015,
		"email_missing_rate": 0.08,
		"phone_missing_rate": 0.10,
		"address_noise_rate": 0.025,
		"postal_code_noise_rate": 0.008,
		"cross_registration_shift_prob": 0.10,
		"cross_registration_shift_max_days": 30,
		"pin_corruption_rate": 0.0003,
	},
	"EPD_B": {
		"name_noise_rate": 0.03,
		"email_missing_rate": 0.14,
		"phone_missing_rate": 0.16,
		"address_noise_rate": 0.05,
		"postal_code_noise_rate": 0.018,
		"cross_registration_shift_prob": 0.35,
		"cross_registration_shift_max_days": 60,
		"pin_corruption_rate": 0.0008,
	},
	"EPD_C": {
		"name_noise_rate": 0.05,
		"email_missing_rate": 0.22,
		"phone_missing_rate": 0.24,
		"address_noise_rate": 0.08,
		"postal_code_noise_rate": 0.03,
		"cross_registration_shift_prob": 0.50,
		"cross_registration_shift_max_days": 120,
		"pin_corruption_rate": 0.0015,
	},
}

# Extra variance on overlapping records from another source.
CROSS_SOURCE_VARIANT_RATES = {
	"EPD_A": 0.01,
	"EPD_B": 0.02,
	"EPD_C": 0.03,
}

INTRA_SOURCE_DUP_RATES = {
	"EPD_A": 0.004,
	"EPD_B": 0.009,
	"EPD_C": 0.016,
}

FALSE_POSITIVE_RATES = {
	"EPD_A": 0.0015,
	"EPD_B": 0.0025,
	"EPD_C": 0.0035,
}
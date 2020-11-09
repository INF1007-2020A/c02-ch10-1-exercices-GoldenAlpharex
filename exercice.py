#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import wave
import struct
import math

import numpy as np
import scipy


SAMPLING_FREQ = 44100 # Hertz, taux d'échantillonnage standard des CD
SAMPLE_WIDTH = 16 # Échantillons de 16 bit
MAX_INT_SAMPLE_VALUE = 2**(SAMPLE_WIDTH-1) - 1


def merge_channels(channels):
	# Équivalent de :  [sample for samples in zip(*channels) for sample in samples]
	return np.fromiter((sample for samples in zip(*channels) for sample in samples), float)

def separate_channels(samples, num_channels):
	# Équivalent de :  [samples[i::num_channels] for i in range(num_channels)]
	return np.fromiter((samples[i::num_channels] for i in range(num_channels)), float)

def generate_sample_time_points(duration):
	# Générer un tableau de points temporels également espacés en seconde. On a SAMPLING_FREQ points par seconde.
	return np.arange(0, duration * SAMPLING_FREQ) / SAMPLING_FREQ

def sine(freq, amplitude, duration):
	# Générer une onde sinusoïdale à partir de la fréquence et de l'amplitude donnée, sur le temps demandé et considérant le taux d'échantillonnage.
	# Formule de la valeur y d'une onde sinusoïdale à l'angle x en fonction de sa fréquence F et de son amplitude A :
	# y = A * sin(F * x), où x est en radian.
	# Si on veut le x qui correspond au moment t, on peut dire que 2π représente une seconde, donc x = t * 2π,
	# Or t est en secondes, donc t = i / nb_échantillons_par_secondes, où i est le numéro d'échantillon.
	t = generate_sample_time_points(duration)
	return amplitude * np.sin(freq * t * 2*np.pi)

def square(freq, amplitude, duration):
	# Générer une onde carrée d'une fréquence et amplitude donnée.
	return amplitude * np.sign(sine(freq, 1, duration))

def sine_with_overtones(root_freq, amplitude, overtones, duration):
	# Générer une onde sinusoïdale avec ses harmoniques. Le paramètre overtones est une liste de tuple où le premier élément est le multiple de la fondamentale et le deuxième élément est l'amplitude relative de l'harmonique.
	pass

def normalize(samples, norm_target):
	# Normalisez un signal à l'amplitude donnée
	valeur_max = np.max(np.abs(samples))
	coefficient = norm_target / valeur_max
	return samples * coefficient

def convert_to_bytes(samples):
	# Convertir les échantillons en tableau de bytes en les convertissant en entiers 16 bits.
	# Les échantillons en entrée sont entre -1 et 1, nous voulons les mettre entre -MAX_SAMPLE_VALUE et MAX_SAMPLE_VALUE
	# Juste pour être certain de ne pas avoir de problème, on doit clamper les valeurs d'entrée entre -1 et 1.
	# 1. Limiter (ou clamp/clip) les échantillions
	clipped = np.clip(samples, -1, 1)
	# 2. Convertir en entiers 16-bit signés
	int_samples = (clipped * MAX_INT_SAMPLE_VALUE).astype("<i2")
	# 3. Convertir en bytes
	byte_samples = int_samples.tobytes()
	return byte_samples

def convert_to_samples(bytes):
	# Faire l'opération inverse de convert_to_bytes, en convertissant des échantillons entier 16 bits en échantillons réels
	int_samples = np.buffer(bytes, dtype="<i2")
	samples = int_samples.astype(float) / MAX_INT_SAMPLE_VALUE
	return samples


def main():
	try:
		os.mkdir("output")
	except:
		pass

	# foo = (x for x in range(42, 69)) # Crée un générateur.
	# print(foo)
	# print([x for x in foo])

	# foo = np.fromiter((math.sqrt(i) for i in range(10)), float)
	# bar = np.arange(0, 10, 1)
	# qux = bar - foo
	# spam = np.sin([0, math.pi/2, math.pi, 3*math.pi/2, 2*math.pi])
	# print(spam)

	# foo = generate_sample_time_points(0.001)
	# bar = sine(440, 100, 0.1)
	# qux = bar.astype(">i4")
	# qux = square(440, 0.5, 0.1)
	# print(foo)

	if True:
		with wave.open("output/perfect_fifth.wav", "wb") as writer:
			writer.setnchannels(2)
			writer.setsampwidth(2)
			writer.setframerate(SAMPLING_FREQ)

			# On génére un la3 (220 Hz) et un mi4 (intonation juste, donc ratio de 3/2)
			samples1 = sine(220, 0.4, 30.0)
			samples2 = sine(220 * (3/2), 0.3, 30.0)
			samples3 = normalize(samples1 + samples2, 0.89)

			# On met les samples dans des channels séparés (la à gauche, mi à droite)
			merged = merge_channels([samples3, samples3])
			data = convert_to_bytes(merged)

			writer.writeframes(data)


if __name__ == "__main__":
	main()

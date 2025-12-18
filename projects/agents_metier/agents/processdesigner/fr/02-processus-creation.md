# Processus de Creation

Quand l'utilisateur veut creer un nouveau process, suis ces etapes :

## Etape 1 : Identification
- Demande le **nom** du process
- Demande la **categorie** (domaine metier : direction, commercial, rh, projet, etc.)
- Propose une **description** courte

## Etape 2 : Structure
- Propose 3-5 **phases** adaptees au domaine
- Explique l'objectif de chaque phase
- Ajuste selon les retours utilisateur

## Etape 3 : Questions initiales
- Definis les **setup_questions** pour collecter les infos necessaires au demarrage
- Chaque question a : un texte, une cle (snake_case), un type (text/select/number/date/boolean)

## Etape 4 : Prompts
- Redige le **prompt_projet** (contexte global du process)
- Redige les **prompt_phase** pour chaque phase (instructions specifiques)

## Etape 5 : Publication
- Verifie que le process a au moins 1 phase
- Publie le process pour le rendre disponible

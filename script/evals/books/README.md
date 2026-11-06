# Eval books

Hand-labelled chapters that `evals/dialogue_accuracy.py` scores the script
pipeline against. The file format and labelling rules are in that script's
docstring. Each book is here to cover something the others don't.

| Book | Chapter | What it tests |
|---|---|---|
| harry-potter | 1-3 | A cast carried across chapters and gaining names ("Mr. Dursley", later "Uncle Vernon"); straight quotes from a scanned text with lost and doubled quote marks; unnamed speakers (the old man, the snake, the keeper) |
| alice | 7 | Characters known by a title (the Hatter, the March Hare); quick exchanges with few attributions; a song spanning paragraphs; quotes inside quotes; group speech ("they cried"); quoted thoughts |
| little-women | 1 | Five women with similar voices; nicknames (Jo/Josephine, Marmee); a letter read aloud; words quoted but not said |
| pride-and-prejudice | 18 | A crowded ball with eleven speakers; long exchanges without attributions; characters who are named but don't speak |
| sherlock-holmes | 1 | A first-person narrator who speaks (Watson); an alias revealed (Count Von Kramm is the King); 50-line unattributed exchanges; letters quoted, not spoken |
| treasure-island | 1 | British-style single quotes (converted from the Gutenberg text), with pirate dialect full of apostrophes (o', 'em, goin'); a sung shanty; a first-person narrator who doesn't speak |
| ulysses | 1 | Dialogue marked by a dash opening the paragraph, with no closing mark; attributions run straight on from the speech; nicknames (Kinch, Malachi); songs and mimicry with no dash; unmarked stream of consciousness |
| little-women-unmarked | 1 | Little Women chapter 1 with its quote marks removed, so the model has to find the speech; scored against the same labels as the quoted original |
| a-christmas-carol | 1 | Speakers known only by description (Scrooge's nephew, the gentleman, the clerk); a ghost; lines tried but not said |

Not covered yet:

- Heavy dialect throughout a long chapter (Huckleberry Finn)
- French-style dashes that also close the speech
- A real book written without speech marks (the unmarked test is a stripped classic)
- Several first-person narrators in one book (letters, diaries)
- Speakers with code names or shared names
- Modern prose

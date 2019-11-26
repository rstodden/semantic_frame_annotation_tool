# A minimal example of datasets used for the SemEval 2019 Task 2 on Unsupervised Lexical Frame Induction
(NOTE: A valid evaluation license from LDC is required to obtain the full trial-golad dataset and the dependency parses etc.

# What is in this archive file:
	**** Input parse trees in UD format **********
	1. ptb-ud-sentences.conllu: contains an automatic parse of PTB sentences in the UD format. Most importantly, the "assigned ids to sentences" and "positions to tokens" are used to map annotations/frame-structures to sentences 
	and vice versa. Note that we mark only the head of constituents for mapping verbs and their arguments to gold annotations. 
	
	**** GOLD annotations **********
	2. gold/task-1.txt: contains the gold annotations for the subtask 1, i.e., grouping verbs into frames. Apart from a small trial/development set, this gold annotations will not be available to participants untill the end of the post-evaluation period (alost applicable to the following gold datasets).
	3 gold/task-2.1.txt: contains the gold annotations for the subtask 2.1, i.e., grouping verbs their arguments to frames and frame-specific slots.
	4. gold/task-2.2.txt: contains the gold annotations for the subtask 2.2, i.e., grouping arguments of verbs to semantic role clusters. 
	
	**** Expected test files **********
	For all the test data, participants must replace the "UKN" keyword with their system generated cluster-ids 
	5. test/task-1.txt: has exact shape as gold/task-1.txt
	6. test/task-2.1.txt: has exact shape as gold/task-2.1.txt
	7. test/task-2.2.txt: has exact shape as gold/task-2.2.txt
	
	
Note that the shape of arguemnet structures in task-2.1.txt and task-2.2.txt are not necessarily the same.

For more information, visit the codalab page: https://competitions.codalab.org/competitions/19159
	
		
 
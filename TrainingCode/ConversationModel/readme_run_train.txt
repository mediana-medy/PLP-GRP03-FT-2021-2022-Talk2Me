#1. Splitting data (ESConv.json) and output train.txt, valid.txt and test.txt
#process.py
#python process.py


#2. Preprocess the training data, output to ./DATA/{inputter_name}.{config_name}
#prepare.py
#python prepare.py


#3. Training the model
#train.py
#python train.py --config_name strat --inputter_name strat --eval_input_file ./_reformat/valid.txt --seed 13 --max_input_length 160 --max_decoder_input_length 40 --train_batch_size 16 --gradient_accumulation_steps 1 --eval_batch_size 16 --learning_rate 3e-5 --num_epochs 2 --warmup_steps 100 --fp16 false --loss_scale 0.0 --pbar true


#4. Perform Model Inference and Evaluation
#infer.py
#python infer.py --config_name strat --inputter_name strat --add_nlg_eval --seed 0 --load_checkpoint ./DATA/strat.strat/2022-03-15185126.1e-05.2.1gpu/epoch-1.bin --fp16 false --max_input_length 160 --max_decoder_input_length 40 --max_length 40 --min_length 10 --infer_batch_size 2 --infer_input_file ./_reformat/test.txt --temperature 0.7 --top_k 0 --top_p 0.9 --num_beams 1 --repetition_penalty 1 --no_repeat_ngram_size 0

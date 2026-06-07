<p align="center" width="100%">
<img src="https://github.com/user-attachments/assets/d931d4a7-fb5d-4b9c-af54-12bdc875f8e1" width="80%" alt="longwriter">
</p>

# LongWriter: Unleashing 10,000+ Word Generation From Long Context LLMs

<p align="center">
    🤗 <a href="https://huggingface.co/datasets/THUDM/LongWriter-6k" target="_blank">HF Repo</a> • 📃 <a href="https://arxiv.org/abs/2408.07055" target="_blank">Paper</a> • 🚀 <a href="https://huggingface.co/spaces/THUDM/LongWriter" target="_blank">HF Space</a>
</p>

[English](./README.md) | [中文](./README_zh.md) | [日本語](./README_jp.md)

https://github.com/user-attachments/assets/c7eedeca-98ed-43ec-8619-25137987bcde

Left: LongWriter-glm4-9b; Right: GLM-4-9B-chat

## 🔥 Updates
**[2024/08/18]** You can now deploy the LongWriter model using [vllm](https://github.com/vllm-project/vllm). Refer to the code in [vllm_inference.py](https://github.com/THUDM/LongWriter/blob/main/vllm_inference.py) and experience lightning-fast generation. It can **generate over 10,000+ words in just one minute**!

## 🔍 Table of Contents
- [⚙️ LongWriter Deployment](#deployment)
- [✍️ Local Creative Studio](#local-creative-studio)
- [🤖️ AgentWrite](#agentwrite)
- [🖥️ Model Training](#longwriter-training)
- [📊 Evaluation](#evaluation)
- [👀 Cases](#case)
- [📝 Citation](#citation)

<a name="deployment"></a>
## ⚙️ LongWriter Deployment

**Environmental Setup**:
We recommend using `transformers>=4.43.0` to successfully deploy our models.

We open-source two models: [LongWriter-glm4-9b](https://huggingface.co/THUDM/LongWriter-glm4-9b) and [LongWriter-llama3.1-8b](https://huggingface.co/THUDM/LongWriter-llama3.1-8b), trained based on [GLM-4-9B](https://huggingface.co/THUDM/glm-4-9b) and [Meta-Llama-3.1-8B](https://huggingface.co/meta-llama/Meta-Llama-3.1-8B), respectively. These two models point to the "LongWriter-9B-DPO" and "LongWriter-8B" models in our paper. Try the model:
```python
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch
tokenizer = AutoTokenizer.from_pretrained("THUDM/LongWriter-glm4-9b", trust_remote_code=True)
model = AutoModelForCausalLM.from_pretrained("THUDM/LongWriter-glm4-9b", torch_dtype=torch.bfloat16, trust_remote_code=True, device_map="auto")
model = model.eval()
query = "Write a 10000-word China travel guide"
response, history = model.chat(tokenizer, query, history=[], max_new_tokens=32768, temperature=0.5)
print(response)
```
You may deploy your own LongWriter chatbot (like the one we show in the teasor video) by running
```
CUDA_VISIBLE_DEVICES=0 python trans_web_demo.py
```
Alternatively, you can deploy the model with [vllm](https://github.com/vllm-project/vllm), which allows generating 10,000+ words within a minute! See the code example in [vllm_inference.py](https://github.com/THUDM/LongWriter/blob/main/vllm_inference.py).

<a name="local-creative-studio"></a>
## ✍️ Local Creative Studio

This repository now includes a local-first creative writing app under [`graphic_novel_ai/`](./graphic_novel_ai/). It combines LongWriter's long-form generation focus with a multi-agent studio for planning, drafting, polishing, and exporting graphic novel projects on your own machine.

Quick start:

```bash
python3 -m graphic_novel_ai --init-templates
python3 -m graphic_novel_ai --brief graphic_novel_ai_templates/brief.example.json --profile rtx3070
```

The studio supports role-based story agents, Ollama model routing, CLI and GUI entrypoints, Markdown/JSON/Fountain/FDX/storyboard PDF exports, and optional local image-preview hooks. See [`graphic_novel_ai/README.md`](./graphic_novel_ai/README.md) for setup and usage.

For the combined LongWriter + Nove AI Local product direction and recommended next features, see [`docs/COHESIVE_APP_ROADMAP.md`](./docs/COHESIVE_APP_ROADMAP.md).

<a name="agentwrite"></a>
## 🤖️ AgentWrite

![agentwrite](https://github.com/user-attachments/assets/5d80314b-eab6-4945-848d-0db8e23ffc90)

We are also open-sourcing AgentWrite under `agentwrite/`, our automated ultra-long output data construction pipeline. Run `plan.py` and then `write.py` to obtain the final data. Please configure your API key in the files.


<a name="longwriter-training"></a>
## 🖥️ Model Training

You can download and save the **LongWriter-6k** data through the Hugging Face datasets ([🤗 HF Repo](https://huggingface.co/datasets/THUDM/LongWriter-6k)):
```python
dataset = load_dataset('THUDM/LongWriter-6k')
for split, split_dataset in dataset.items():
    split_dataset.to_json("train/LongWriter-6k.jsonl")
```
You can mix it with your own general SFT data. We adopt the code and environment in [LongAlign](https://github.com/THUDM/LongAlign) for model training (we use `transformers==4.43.0` for training on Llama-3.1), with slight modification to adapt to new models. The training code is under `train/`. Please make sure to install FlashAttention 2 according to the code base of [FlashAttention](https://github.com/Dao-AILab/flash-attention).

<a name="evaluation"></a>
## 📊 Evaluation
We introduce two evaluation benchmarks: **LongBench-Write** and **LongWrite-Ruler**. **LongBench-Write** focuses more on measuring the long output quality as well as the output length, while **LongWrite-Ruler** is designed as a light-weight stress test of the model's maximum output length.
We provide our evaluation data and code under `evaluation/`. Run
```bash
CUDA_VISIBLE_DEVICES=0,1,2,3,4,5,6,7 python pred.py
```
to get model responses. Then run `python eval_quality.py` and `python eval_length.py` to evaluate the quality ($S_q$) and length ($S_l$) scores. Remember to configure your OpenAI API key in `eval_quality.py` since we adopt GPT-4o as the judge.

Here are the evaluation results on **LongBench-Write**:
<img width="1000" alt="longbench-write" src="https://github.com/user-attachments/assets/8dbb6c02-09c4-4319-bd38-f1135457cd25">
Here are the evaluation results on **LongWrite-Ruler**:
![longwrite-ruler](https://github.com/user-attachments/assets/471f6e74-ab2c-4ad7-b73f-9ec8d2c2cde5)


<a name="case"></a>
## 👀 Cases
Here are LongWriter-glm4-9b's outputs to random test prompts.

*User: Write a tragic love story about a lord's daughter falling in love with a servant, 5000 words.*
<details>
<summary>Assistant: (6176 words)</summary>
<div style="max-height: 200px; overflow-y: auto; padding: 10px; border: 1px solid #e1e4e8; border-radius: 6px;">

### The Aristocratic Estate

Nestled amidst the rolling hills of the English countryside, the grand estate of Lord Edward Ashwood was a beacon of elegance and sophistication. The sprawling manor, with its towering spires and expansive gardens, stood as a testament to centuries of wealth and power. The Ashwood family, known for their noble lineage and impeccable manners, had been pillars of the local community for generations. The grand halls were filled with the scent of polished wood and rich fabrics, echoing with the soft hum of servants attending to their masters' every need.

Lady Ashwood, the matriarch of the household, was a woman of grace and wisdom. Her beauty had faded with time, but her elegance remained untarnished. She was known for her charitable works and her ability to command respect and admiration from all who met her. Her daughters, Eliza and Arabella, were the epitome of aristocratic charm. Eliza, the elder, was a poised and intelligent young woman, often seen with a book in hand or engaged in scholarly discussions. Arabella, the younger, was vivacious and lively, her laughter ringing through the halls like a bell. Both girls were expected to marry well, their futures already mapped out by their parents.

The household was a bustling hive of activity. The grand dining hall was a testament to the family's wealth, adorned with intricate tapestries and fine china. The servants moved with practiced precision, their duties meticulously assigned. The butler, Mr. Blackwood, was a stern but fair man, ensuring that every aspect of the household ran smoothly. The head cook, Mrs. Brown, was a master of her craft, her culinary skills renowned throughout the county. The young page boys and maids scurried about, their faces a mix of innocence and the early signs of budding adulthood.

The Ashwood estate was a world apart from the simpler lives of the villagers who worked the surrounding lands. The gulf between the two worlds was vast and unbridgeable, a chasm that no one dared to cross. The servants, though integral to the estate's operation, were kept at a distance, their presence a mere background to the grandeur that defined the Ashwoods.

In this world of opulence and order, the seeds of a tragic love story were about to be sown.

### The Hidden Heart of Eliza

Eliza Ashwood was the embodiment of aristocratic grace, her every movement a testament to years of refinement and education. Yet, beneath her composed exterior lay a heart yearning for something more, something the grand estate could not provide. Eliza was not merely a bookish daughter, though her love for literature was well-known. She possessed a depth of thought and a sensitivity that set her apart from her peers. Her days were filled with the routine of the estate—participating in social gatherings, learning the intricacies of diplomacy and etiquette, and engaging in scholarly pursuits. But her nights were often spent in quiet reflection, her mind wandering to thoughts that were far removed from the expectations of her station.

Eliza's interest in the estate's servants was a well-guarded secret. She often found herself drawn to the quieter corners of the manor, where the servants conducted their duties with a sense of quiet dignity. It was during one such moment, while taking a solitary walk through the estate's expansive gardens, that she first encountered Thomas. He was a young servant, tasked with tending to the roses that lined the estate's perimeter. His back was to her as he worked, his hands deftly pruning the delicate blooms. Eliza was captivated by the ease and precision with which he moved, a stark contrast to the hurried chaos of the household's daily operations.

As she watched him, a sense of tranquility washed over her. For the first time in what felt like an eternity, Eliza felt a sense of peace. Thomas's presence was unassuming, his focus entirely on his work. It was a stark contrast to the constant hustle and bustle of the manor. Eliza found herself lingering, her curiosity piqued by the man who seemed to exist in a world of his own, untouched by the grandeur that surrounded him.

Their first conversation was innocent and brief, a simple exchange over the health of Thomas's mother. Eliza's genuine concern and Thomas's humble gratitude left an impression on both of them. From that moment, their interactions became more frequent, though always under the watchful eyes of the household. Eliza would often find herself seeking out Thomas, her heart fluttering with a mix of excitement and fear. Their conversations were simple and heartfelt, often centered around the beauty of the garden or the weather. Yet, it was enough to kindle a flame in Eliza's heart, a flame that she knew she must keep hidden.

Eliza's feelings for Thomas were a source of both comfort and conflict. On one hand, he represented a connection to a simpler, more genuine world, a world where she felt truly seen and understood. On the other hand, she was acutely aware of the social and economic chasm that separated them. The idea of a relationship with a servant was not only unimaginable but also scandalous. Eliza's heart was a battlefield of hope and despair, torn between her desire for love and her duty to her family and society.

As their bond deepened, Eliza found herself questioning her place in the world. She had been raised to aspire to greatness, to marry a man of equal or greater status, to uphold the Ashwood legacy. Yet, here she was, falling in love with a servant, a man who represented everything her world sought to exclude. It was a love that defied logic and reason, a love that threatened to upend the carefully constructed life she had been destined to lead.

Eliza's secret affection for Thomas was a delicate balance, a fragile thread that she clung to with all her might. She knew that revealing her feelings would not only shatter her own dreams but also bring disgrace upon her family. Yet, the more time she spent with Thomas, the more she realized that her heart could no longer be contained. It was a love that was as beautiful as it was dangerous, a love that would test the very foundations of her world.

### Thomas's Hidden Life

Thomas had been born into a family of humble means, his parents working the fields to make ends meet. From a young age, he had known the hardships of rural life, the backbreaking labor and the sting of poverty. Yet, it was not the struggle that defined him but the resilience and determination he found within himself. When the Ashwood estate advertised for new servants, Thomas saw it as an opportunity to escape the confines of his village and forge a better future for himself.

Life at the Ashwood estate was a stark contrast to his previous existence. The grandeur and opulence were overwhelming at first, but Thomas adapted quickly, his innate sense of duty driving him to excel in his duties. He was assigned to the garden, a role that suited his quiet nature and love for the natural world. Each day, he moved through the estate with a sense of purpose, his hands deftly tending to the plants, his mind a sanctuary of calm amidst the chaos.

Despite the differences in their worlds, Thomas felt a strange sense of belonging at the Ashwood estate. The grand halls and ornate decorations were a world apart from his simple upbringing, but there was a certain elegance to the place that he found comforting. The strict routines and the disciplined lives of the servants provided a structure that he had always craved. He found solace in the predictability of his tasks, in the rhythm of his workday that allowed him moments of quiet reflection.

It was during these moments of solitude that Thomas began to notice Eliza. Her presence was like a gentle breeze through the garden, her elegance contrasting with the rustic beauty of the flowers she admired. Thomas was initially drawn to her beauty, but as their interactions grew, he came to appreciate her intelligence and kindness. Eliza was unlike anyone he had ever met, her conversations filled with wisdom and compassion. She saw beyond his station, into the person he truly was.

Their bond grew slowly, built on shared moments of understanding and mutual respect. Thomas found himself looking forward to their brief conversations, his heart lightening with each encounter. Eliza's genuine interest in his life and her willingness to see past the societal barriers that separated them filled him with a sense of hope he had long thought lost. For the first time, Thomas felt valued and seen, not as a servant, but as a person with dreams and aspirations of his own.

Yet, Thomas was acutely aware of the dangers that their relationship posed. He knew the social and economic chasm that separated them, the impossibility of a future together. The idea of love was a fragile dream in a world that demanded conformity and respectability. Thomas's heart was a battlefield of hope and fear, torn between his desire for Eliza and the reality of their circumstances. He loved her with all his heart, but he was also pragmatic, understanding that their love was a risk he could not afford to take.

As their bond deepened, Thomas found himself questioning his place in the world. He had come to the Ashwood estate seeking a better life, but now he found himself caught in a web of emotions that threatened to unravel everything he had worked for. The love he felt for Eliza was a beautiful but dangerous distraction, a reminder of the dreams he dared not speak aloud. He knew that their love was a fragile thread, one that could easily be severed by the harsh realities of their world.

Thomas's heart was a sanctuary of love and fear, a place where his dreams and reality clashed. He loved Eliza with a passion that defied reason, but he was also realistic, understanding that their love was a fragile hope in a world that demanded conformity. As their bond grew stronger, Thomas found himself standing at a crossroads, his future uncertain and his heart in turmoil. He knew that his love for Eliza was a risk he was willing to take, but he was also aware of the dangers that lay ahead.

### The Unspoken Bond

The bond between Eliza and Thomas grew stronger with each passing day, a silent yet powerful connection that neither could deny. Their conversations, though brief, were filled with a depth of understanding that transcended the barriers of their social standing. Eliza found herself looking forward to their encounters, each interaction a source of solace and joy in her otherwise structured and rigid world. Thomas, in turn, felt a sense of belonging and purpose that he had never known before, Eliza's presence a beacon of hope in his otherwise monotonous life.

One evening, as the sun dipped below the horizon, casting a golden glow over the garden, Eliza found herself once again drawn to the roses Thomas tended. This time, she approached him with a quiet determination. "Thomas," she began, her voice barely above a whisper, "I wanted to thank you for always being there, for listening to me when no one else would."

Thomas looked up, his eyes meeting hers with a mixture of surprise and gratitude. "It's my pleasure, Miss Eliza. You've always been kind to me."

Eliza took a deep breath, her heart pounding in her chest. "Thomas, there's something I need to tell you. I... I care for you deeply. More than just as a friend or a servant. I... I love you."

Thomas's eyes widened, his heart racing at the weight of her words. He had felt the same but had never dared to voice them, afraid of the consequences. "Eliza," he whispered, his voice trembling, "I... I feel the same. But we both know the dangers of what we feel."

Eliza's eyes filled with a mixture of hope and despair. "I know the risks, Thomas. I've thought about it night and day. But I can't deny my feelings any longer. I need you to know how I truly feel."

Thomas's heart ached with the weight of her words. He loved her with every part of his being, but the reality of their situation loomed large. "Eliza, we come from two different worlds. The gap between us is vast and unbridgeable. If we pursue this, we risk everything—our futures, our families, our very lives."

Eliza's eyes glistened with unshed tears. "I understand that, Thomas. But I can't live without you. I need you in my life, even if it means defying everything I've ever been taught."

Thomas took a step closer, his hand reaching out to gently touch her cheek. "Eliza, you mean more to me than words can express. But we must be careful. The world is not kind to those who defy its rules."

Eliza nodded, her heart heavy with the weight of their reality. "I know, Thomas. But I'm willing to face whatever comes. I love you, and I can't let that go."

Their fingers brushed against each other's, a silent promise of the love they shared. It was a love that defied reason and societal norms, a love that both terrified and inspired them. They knew the risks, but they were also aware of the beauty and depth of the bond they had forged.

As they stood there under the golden light of the setting sun, their hearts beat in unison, a testament to the love that had grown between them. They were two souls entwined by fate, their love a fragile yet resilient thread that defied the world's expectations. Together, they faced the uncertainties of their future, their hearts united by a love that was as powerful as it was dangerous.

### The Struggle Within

Eliza's heart was a tempest of emotions, torn between her love for Thomas and the societal expectations that loomed over her. She knew that her feelings for Thomas were real, profound, and unshakable. Yet, the weight of her upbringing and the expectations of her family were a constant reminder of the peril she faced. Every day was a battle within herself, a struggle to reconcile her heart with her duty.

Eliza's parents had always been strict in their expectations, instilling in her a sense of responsibility and obligation to the Ashwood legacy. They had planned her future, envisioning a marriage that would secure the family's status and wealth. The idea of defying those plans, of pursuing a love that defied societal norms, was a terrifying prospect. Eliza feared the disgrace that would come to her family, the ruin of her carefully constructed life.

Yet, every moment spent with Thomas only deepened her resolve. His kindness, his intelligence, and his unwavering support filled a void in her heart that nothing else could. Eliza found herself longing for the simple, genuine moments they shared, the comfort of his presence and the joy that his love brought into her life. She realized that her happiness, her true happiness, lay in the love she felt for Thomas, not in the expectations of her family.

Eliza's internal conflict was a relentless torment. She loved her family and respected their wishes, but she also loved Thomas with a passion that she could no longer ignore. She spent sleepless nights wrestling with her emotions, her mind a whirlwind of doubt and determination. She knew that she could not continue living a lie, that she had to make a choice between her heart and her duty.

One evening, as she stood before her mirror, staring at her reflection, Eliza made a decision. She would speak to her parents, reveal her feelings for Thomas, and face the consequences. She knew it would be a difficult conversation, but she also knew that she could no longer live in silence. She owed it to herself and to Thomas to be honest about her heart.

As she prepared to face her parents, Eliza's heart was filled with a mixture of fear and hope. She was ready to fight for her love, to defy the expectations that had been laid out for her. She was willing to face whatever consequences might come, as long as she could be true to herself and to the man who had captured her heart.

### The Heart-Wrenching Confession

Eliza took a deep breath, steeling herself for the conversation that was about to unfold. She found her parents in the drawing room, their faces a mask of calm as they sipped their tea. Eliza's heart pounded in her chest as she approached them, her hands trembling slightly. "Father, Mother," she began, her voice steady but filled with emotion, "I need to talk to you about something important."

Lady Ashwood set down her teacup, her eyes narrowing slightly. "What is it, Eliza? Out with it."

Eliza took a deep breath, her eyes meeting her parents' with a mixture of determination and fear. "I... I have something to confess. I... I am in love."

Both of her parents' faces paled, their expressions shifting from surprise to concern. Lord Ashwood's stern gaze softened slightly, while Lady Ashwood's eyes filled with a mixture of shock and worry. "Eliza, what do you mean? With whom?" Her voice was a hushed whisper, as if speaking too loudly might shatter the fragile reality they all lived in.

Eliza's heart ached as she forced herself to speak the words that had been burning in her chest for so long. "I am in love with Thomas, the servant who tends the garden. I... I can't deny it any longer. I love him with all my heart."

The room fell into a heavy silence, the air thick with the weight of unspoken words. Lord Ashwood's face darkened, his eyes narrowing as he absorbed her words. "Thomas? The servant? Eliza, this is unthinkable. How could you even entertain such a notion?"

Lady Ashwood's eyes filled with tears, her voice trembling. "Eliza, you must be mistaken. This cannot be real. You must forget him immediately."

Eliza's heart broke as she looked at her parents, seeing the pain and disappointment in their eyes. She knew that their reaction was inevitable, but the words still felt like a dagger to her soul. "I am not mistaken, Mother. I am in love with Thomas, and I cannot change that. I... I cannot live a lie any longer."

Lord Ashwood's voice was cold and stern. "Eliza, you must understand the consequences of your actions. This is not just about you. It is about the Ashwood legacy, about our reputation and honor. You cannot throw all of that away for a mere servant."

Eliza's eyes filled with tears, her heart aching with the weight of their words. "I know, Father. I know the risks. But I cannot live without Thomas. He has given me a love that I never thought possible, a love that makes me feel alive. I cannot deny my feelings any longer."

Lady Ashwood's voice broke, her tears flowing freely. "Eliza, you don't understand. This is more than just a love affair. It is a betrayal of everything we stand for. You are putting our entire family at risk."

Eliza's heart was in turmoil, torn between her love for Thomas and her duty to her family. She knew that her parents were right, that the consequences of her actions could be devastating. But she also knew that she could not live a life of lies, that she had to be true to herself and to the man who had captured her heart.

As the conversation continued, Eliza's resolve only strengthened. She knew that she would face consequences, but she was willing to bear them. She would fight for her love, even if it meant losing everything.

### The Unraveling of Dreams

The days following Eliza's confession were a whirlwind of turmoil and heartache. Lord and Lady Ashwood were determined to put an end to what they saw as a scandalous relationship, and their actions were swift and unforgiving. Eliza was forbidden from seeing Thomas, her movements closely monitored by the household staff. The garden, once a sanctuary for their secret meetings, became a place of dread, its beauty marred by the weight of their separation.

Eliza's heart was in shambles, each day a painful reminder of the love she had been forced to abandon. She spent her nights in tears, her mind a constant echo of the words spoken by her parents. The walls of the grand estate seemed to close in around her, the once familiar surroundings now a prison of her own making. Her once vibrant spirit dimmed, her laughter replaced by a hollow echo of its former self.

Thomas, too, was not immune to the devastation. He could sense the change in Eliza, the sadness that clouded her eyes and weighed heavily on her heart. He longed to reach out to her, to offer her the comfort she so desperately needed, but he knew that any attempt would only worsen her situation. His heart ached with every passing day, his love for Eliza a silent but relentless torment.

The household was abuzz with the news of Eliza's forbidden love, the servants whispering behind closed doors and the guests at social gatherings casting judgmental glances her way. Eliza's reputation was under siege, her once impeccable standing now tarnished by the scandal. The pressure was immense, and she found herself questioning her every action, her every decision.

Despite the distance imposed upon them, Eliza and Thomas found ways to communicate. Secret notes were passed through the estate, their words a lifeline in the storm of their separation. Each letter was a balm to their wounded hearts, a reminder of the love that had once brought them together. But even these brief exchanges were fraught with danger, each note a potential discovery that could lead to even greater consequences.

Eliza's parents, relentless in their efforts to break her spirit, increased the pressure. They sought to distract her with social engagements and scholarly pursuits, hoping to divert her attention from Thomas. But Eliza's heart remained steadfast, her love for Thomas an unyielding force that defied their attempts to sever their bond.

The strain of their situation began to take its toll on Eliza's health. She grew pale and weak, her once vibrant energy sapped by the emotional and physical weight of her plight. The Ashwood estate, once a symbol of her family's power and prestige, now felt like a gilded cage, confining her spirit and threatening to crush her soul.

Thomas, watching from a distance, felt the same despair. He saw the pain in Eliza's eyes, the way her once bright smile had faded into a shadow of its former self. His heart ached with every passing day, his love for her a beacon of hope in the darkness that had enveloped her life.

As the days turned into weeks, the love between Eliza and Thomas remained unbroken, a testament to their unwavering devotion to each other. They faced their trials with courage and resilience, their bond stronger for the hardships they endured. But the weight of their circumstances was a constant reminder of the dangers that loomed over them, a reminder that their love, while powerful, was also fragile and vulnerable to the world's judgment.

### The Breaking Point

The weight of their secret love became too much for Eliza to bear. The constant pressure from her parents, the judgment of society, and the physical and emotional toll of their separation began to erode her spirit. One evening, as the moon cast a silvery glow over the Ashwood estate, Eliza made a desperate decision. She would run away, escape the confines of her life and the expectations that had been laid upon her.

Eliza slipped out of the manor under the cover of darkness, her heart pounding with a mixture of fear and determination. She made her way to the garden, where Thomas had promised to meet her. The garden, once a place of solace, now felt like a battlefield, each step she took a step closer to the unknown.

Thomas was waiting for her, his face a mask of concern and hope. "Eliza, I knew you would come," he whispered, his voice trembling with emotion. "I've been so worried about you."

Eliza's eyes filled with tears as she threw her arms around him, her body shaking with the weight of her emotions. "Thomas, I can't stay any longer. The pressure is too much. I need to be with you, even if it means losing everything."

Thomas held her close, his heart aching with the depth of her words. "Eliza, I understand. I've felt the same. But we must be careful. Running away is not a solution. It will only make things worse."

Eliza pulled back, her eyes searching Thomas's face for reassurance. "I know, Thomas. But I can't go back. I can't live a lie any longer. I need you, and I need to be free to love you."

Thomas's heart broke as he looked into her eyes, seeing the pain and determination that burned within them. He knew that Eliza was right, that running away was not the answer, but he also knew that he could not bear to see her suffer any longer. "Eliza, I love you more than words can express. But we must be smart about this. We need a plan, a way to make a life together without the world's judgment."

Eliza nodded, her tears drying on her cheeks as she took a deep breath. "I trust you, Thomas. I know you will guide me. I just need to be with you, to feel your love and support."

Thomas led Eliza to a secluded part of the garden, away from the prying eyes of the household staff. He took her hands in his, his gaze steady and resolute. "Eliza, I promise you that I will do everything in my power to protect you and to build a life together. But we must be patient, and we must be careful. We cannot rush into anything without a solid plan."

Eliza's heart swelled with hope and love as she looked into Thomas's eyes. "I believe in you, Thomas. I believe that we can find a way, that our love can overcome everything. I just need you."

Thomas's eyes softened as he pulled Eliza into his arms, holding her close as if to shield her from the world's dangers. "I love you, Eliza. More than anything. And I will do whatever it takes to be with you, to build a life that is truly ours. But we must be strong, and we must be smart."

Eliza's heart felt lighter as she rested her head on Thomas's chest, listening to the steady beat of his heart. She knew that their journey would be fraught with challenges, but she also knew that their love was strong enough to overcome them. "I love you too, Thomas. And I will stand by you no matter what."

As they stood there in the moonlit garden, their hearts beating in unison, Eliza and Thomas made a silent vow to each other. They would face the world together, their love a beacon of hope in the darkness. They would fight for their happiness, no matter the cost.

### The Ultimate Sacrifice

The days that followed were a blur of desperation and hope. Eliza and Thomas knew that their time was limited, that the authorities would not be long in finding them. They spent their days in hiding, moving from one safe house to another, always looking over their shoulders for the threat of discovery. Each night, they found solace in each other's arms, their love a fragile yet resilient thread that held them together in the face of adversity.

As the authorities closed in, Eliza and Thomas knew that their time was running out. They had to make a decision, a choice that would determine the course of their lives. Eliza looked into Thomas's eyes, her heart heavy with the weight of their reality. "Thomas," she whispered, her voice trembling, "we can't keep running. They will find us eventually. We need a plan, a way to ensure that our love endures, even if we cannot be together."

Thomas's eyes filled with a mixture of love and sorrow. "Eliza, I have been thinking about this. There is only one way to ensure that our love endures, that our sacrifice is not in vain. We must marry, legally. It is our only chance to be together, to build a life that is truly ours."

Eliza's eyes widened in shock and fear. "Thomas, I can't marry you. It is illegal, and it would mean losing everything—our freedom, our family, our future. I can't ask you to do that."

Thomas's grip on her hand tightened, his voice firm and resolute. "Eliza, you must understand. Marrying me is the only way we can be together, the only way to ensure that our love endures. I am willing to face the consequences, to give up everything for you. But I need you to be with me, to stand by my side."

Eliza's heart ached with the weight of Thomas's words. She knew that he was right, that their love was worth any sacrifice. But the idea of losing everything, of defying society's expectations, was a daunting prospect. "Thomas, I love you more than anything. But I am afraid of what will happen if we marry. I am afraid of losing you, of losing everything we have built together."

Thomas's eyes softened as he pulled Eliza into his arms, holding her close as if to shield her from the world's dangers. "Eliza, you must trust me. I will protect you, I will fight for us. We can make this work, we can build a life together. But we must be brave, and we must be united."

Eliza's heart swelled with love and determination as she looked into Thomas's eyes. She saw the depth of his devotion, the unwavering commitment he had for her. She knew that he was right, that their love was worth any sacrifice. "Thomas, I trust you. I will marry you, and I will stand by your side no matter what."

As they stood there in the dim light of their hidden sanctuary, Eliza and Thomas made their final vow to each other. They would marry, defy society's expectations, and fight for their love. They would face the world together, their hearts united by a love that was as powerful as it was dangerous.

Their wedding was a secret ceremony, held in the early hours of dawn to avoid detection. They exchanged vows in a small, secluded chapel, their hearts beating in unison as they promised to love and support each other through every trial and tribulation. The ceremony was simple but profound, a testament to their love and their commitment to each other.

As they emerged from the chapel, hand in hand, Eliza and Thomas knew that their journey had only just begun. They faced the world with a newfound sense of purpose and determination, their love a beacon of hope in a world that sought to crush them. They were ready to face whatever challenges lay ahead, united by a love that was as powerful as it was fragile.

### The Heart-Wrenching End

The authorities discovered Eliza and Thomas's marriage soon after the ceremony. The news spread like wildfire through the estate and the surrounding villages, igniting a firestorm of outrage and scandal. Lord and Lady Ashwood were devastated, their pride and reputation shattered by their daughter's defiance. Eliza was immediately confined to her room, her parents refusing to speak to her or acknowledge her existence.

Thomas, determined to protect Eliza, stood by her side, his love unwavering despite the danger it posed to him. He was dismissed from his position at the estate, his future prospects ruined. The villagers turned their backs on him, their judgmental stares a constant reminder of the price he had paid for his love.

Eliza's heart was in tatters, her spirit broken by the weight of her parents' rejection and the world's condemnation. She spent her days in solitude, her once vibrant spirit dimmed by the sorrow that enveloped her. Thomas, though strong and resilient, could see the despair in her eyes, the pain that gnawed at her soul.

One evening, as the moon cast a silvery glow over the estate, Thomas took Eliza into the garden, the same place where their love had blossomed. He held her close, his voice trembling with emotion. "Eliza, I am so sorry. I never wanted this to happen. I love you more than anything, and I would do anything to make things right."

Eliza's eyes filled with tears, her voice a whisper. "Thomas, I know. But I can't bear the pain any longer. I can't live in this world of judgment and rejection. I need to be free, to find peace."

Thomas's heart broke as he looked into Eliza's eyes, seeing the pain and determination that burned within them. He knew that she was right, that she needed to be free from the world's constraints. "Eliza, please don't do this. I can't live without you. I love you, and I will always love you."

Eliza pulled back, her eyes searching Thomas's face for one last moment of solace. "Thomas, I love you too. But I need to be free, to find the peace that has eluded me. I am so sorry."

Thomas's heart ached with the weight of Eliza's words. He knew that he could not stop her, that her determination was unwavering. "Eliza, I will always love you, no matter what. But I need you to be happy, to find the peace that you deserve."

Eliza's eyes glistened with unshed tears as she looked into Thomas's eyes, her heart aching with the weight of her decision. "Thomas, I will always love you. And I will never forget the love we shared. I am so sorry for the pain I have caused you."

Thomas's eyes filled with tears as he pulled Eliza into his arms, holding her close as if to shield her from the world's dangers. "Eliza, you have given me the greatest gift of my life—the love of a kind and beautiful soul. I will always cherish that love, no matter what."

As they stood there in the moonlit garden, their hearts beating in unison, Eliza and Thomas made their final farewell. They knew that their love had been powerful and beautiful, a testament to the strength of the human spirit. But they also knew that their love had come at a great cost, a sacrifice that had forever changed their lives.

Eliza took a deep breath, her heart heavy with the weight of her decision. "Thomas, I need to go. I need to find the peace that has eluded me. I will always love you, and I will never forget you."

Thomas's eyes filled with tears as he released Eliza, his heart aching with the weight of her departure. "Eliza, be happy, be free. I will always love you, and I will always remember the love we shared."

Eliza walked away from Thomas, her heart breaking with each step. She knew that she was leaving a piece of her heart behind, that her love for Thomas would forever be a part of her. But she also knew that she needed to find the peace that had eluded her, to build a life that was truly her own.

Thomas watched Eliza disappear into the darkness, his heart aching with the weight of her departure. He knew that their love had been powerful and beautiful, a testament to the strength of the human spirit. But he also knew that their love had come at a great cost, a sacrifice that had forever changed their lives.

As the moon cast its silvery glow over the garden, Eliza and Thomas's love story came to an end. Their love had been powerful and beautiful, a testament to the strength of the human spirit. But it had also been tragic and heartbreaking, a reminder of the dangers that love can face in a world that often seeks to crush it.

</div>
</details>
<br/>

*User: 写一篇10000字的中国旅游指南*
<details>
<summary>Assistant: (10691字)</summary>
<div style="max-height: 200px; overflow-y: auto; padding: 10px; border: 1px solid #e1e4e8; border-radius: 6px;">

### 中国旅游概述

中国，这片古老而神秘的东方土地，拥有着悠久的历史和丰富的文化。作为世界上人口最多的国家之一，中国以其多样的地理景观、独特的文化遗产和热情好客的人民而闻名于世。无论是繁华的都市、壮丽的自然风光，还是深厚的文化底蕴，都吸引着无数游客前来探访。

中国旅游的魅力首先体现在其多样化的地理景观上。从北国风光的雪域高原到南国海滨的碧海蓝天，从西部大漠的辽阔无垠到东部平原的绿意盎然，中国几乎囊括了所有类型的自然景观。游客可以在这里体验到从寒冷到炎热、从干燥到湿润的各种气候和地貌，满足对自然风光的所有想象。

其次，中国的文化遗产是其旅游的一大亮点。中国有着五千多年的文明史，留下了无数珍贵的文化遗产。从宏伟的古代建筑，如长城、故宫、兵马俑，到古老的寺庙和园林，如少林寺、苏州园林，每一个景点都承载着深厚的历史和文化内涵。这些文化遗产不仅是历史的见证，更是中华民族智慧的结晶，吸引着无数游客前来参观和学习。

此外，中国的人民也是其旅游魅力的重要组成部分。中国人民热情好客，乐于助人，让游客在旅途中感受到家的温暖。无论是大城市的热闹街头，还是小村庄的宁静小巷，人们总是愿意分享他们的故事和经验，让游客更好地了解和体验中国的文化。

总之，中国以其独特的自然风光、丰富的文化遗产和热情好客的人民，成为全球游客向往的旅游目的地。无论是历史爱好者、自然探险家还是文化体验者，都能在中国找到属于自己的旅游天堂。

### 中国的行政区划

中国是一个地域辽阔、民族众多的国家，其行政区划复杂多样。全国共有34个省级行政区，包括23个省、5个自治区、4个直辖市和2个特别行政区。每个省级行政区都有其独特的地理、文化和历史背景，为游客提供了丰富多彩的旅游选择。

首先，23个省是中国行政区划中的主体部分。这些省份包括山东、河南、四川、湖南、湖北、江西、广东、广西、贵州、云南、陕西、甘肃、青海、宁夏、新疆等。每个省份都有其独特的自然风光和文化特色。例如，山东省以悠久的历史和丰富的文化遗产著称，拥有泰山、曲阜孔庙等著名景点；河南省则是中华文明的重要发源地，拥有龙门石窟、清明上河园等历史文化景点；四川省以其秀美的自然风光和独特的美食文化闻名，九寨沟、峨眉山等自然景观吸引了大量游客。

其次，5个自治区分别是内蒙古自治区、广西壮族自治区、西藏自治区、宁夏回族自治区和新疆维吾尔自治区。这些自治区以其独特的民族文化和自然景观而著称。例如，内蒙古自治区拥有广袤的草原和壮观的沙漠景观，是骑马和草原探险的理想之地；广西壮族自治区以其秀美的山水和丰富的民族文化而闻名，桂林山水、漓江等自然景观令人陶醉；西藏自治区则是世界屋脊，拥有珠穆朗玛峰、布达拉宫等壮丽的自然和人文景观，是朝圣和探险的绝佳选择。

4个直辖市包括北京、上海、天津和重庆。这些城市都是中国的重要经济、文化和交通中心，拥有丰富的历史遗迹和现代化建筑。例如，北京市是中国的首都，拥有故宫、长城等世界著名的文化遗产；上海市是中国的经济中心，拥有东方明珠塔、外滩等现代化建筑和商业区；天津市则以其独特的港口文化和历史遗迹而闻名；重庆市以其壮丽的山水和独特的火锅文化吸引了大量游客。

最后，2个特别行政区是香港和澳门。这两个城市以其独特的国际化和现代化风貌而著称。香港是国际金融中心和购物天堂，拥有维多利亚港、迪士尼乐园等著名景点；澳门则以其博彩业和葡萄牙殖民历史而闻名，大三巴牌坊、威尼斯人度假村等景点吸引了大量游客。

总之，中国的行政区划复杂多样，每个省级行政区都有其独特的地理、文化和历史背景，为游客提供了丰富多彩的旅游选择。无论是自然风光、历史文化还是现代都市，中国都能满足不同游客的旅游需求。

### 中国的气候特点

中国的气候类型多样，从北到南，从东到西，气候差异显著。总体来说，中国可以分为寒带、温带、亚热带和热带四种主要气候类型。北方地区冬季寒冷，夏季炎热，而南方地区则四季如春，温暖宜人。这种多样的气候特点不仅为中国的农业生产提供了丰富的条件，也为游客提供了多样化的旅游体验。

在北方，冬季寒冷漫长，尤其以东北地区最为典型。哈尔滨的冰雪节吸引了大量游客前来观赏冰雕和体验冰雪运动。夏季则相对短暂，但气温较高，适合避暑旅游。东北地区的大兴安岭、长白山等地区，夏季绿意盎然，是避暑度假的好去处。

中部地区包括华北、华东和华中地区，主要气候类型为温带季风气候。冬季寒冷干燥，夏季炎热多雨。北京、上海和武汉等大城市都位于这一区域。冬季的北京，游客可以参观故宫、长城等著名景点，体验寒冷中的历史文化魅力；夏季的上海，游客可以游览外滩、城隍庙，享受都市的繁华和清凉。

南方地区主要气候类型为亚热带和热带季风气候。这里四季分明，冬季温暖，夏季炎热潮湿。广东、广西、福建和海南等省份都属于这一区域。冬季的海南，温暖如春，是避寒度假的理想之地；夏季的厦门，游客可以游览鼓浪屿、南普陀寺，享受海滨的清凉和美景。

西部地区包括新疆、西藏、青海和甘肃等省份，气候类型多样，从寒带到高原气候都有。新疆的冬季寒冷干燥，夏季则炎热多风，是探险和草原旅游的好去处。西藏的气候则以高原气候为主，冬季寒冷，夏季凉爽，是朝圣和登山的热门目的地。青海湖、茶卡盐湖等自然景观在夏季尤其迷人。

总体来说，中国的气候特点为游客提供了多样化的旅游选择。不同季节的气候条件适合不同的旅游活动，游客可以根据自己的喜好和需求选择合适的旅行时间。例如，冬季适合前往北方和西北地区体验冰雪风光，夏季则适合前往南方和东南沿海地区避暑度假。了解中国的气候特点，有助于游客更好地规划旅行路线，享受愉快的旅程。

### 中国的主要旅游景点

中国拥有众多世界著名的旅游景点，这些景点不仅代表了中国丰富的历史和文化，也展示了其独特的自然风光。以下是一些中国最具代表性的主要旅游景点：

#### 长城

长城，作为中国最著名的象征之一，是世界上最长的军事防御工程。它蜿蜒于中国北方的高山和丘陵之间，全长约21,196公里。游客可以参观多个著名的长城段，如八达岭长城、慕田峪长城和嘉峪关长城。八达岭长城是保存最完整的一段，也是游客最多的地方；慕田峪长城则以其险峻和优美的风景著称；嘉峪关长城则展示了长城的西北风格。无论在哪个季节，长城都是游客拍照和体验中国历史的重要地点。

#### 故宫

故宫，也称为紫禁城，是明朝和清朝两代皇宫，位于北京市中心。这座宏伟的宫殿建筑群占地约72万平方米，拥有9000多间房屋。故宫不仅以其壮观的建筑和精美的装饰闻名，还收藏了大量的珍贵文物和艺术品。游客可以参观太和殿、乾清宫、养心殿等主要建筑，了解中国古代宫廷生活和文化。故宫每年吸引着数百万游客，是了解中国历史和文化的重要窗口。

#### 兵马俑

兵马俑，位于陕西省西安市，是中国古代秦朝的军事遗迹。1974年，兵马俑的发现震惊了世界，成为中国古代文明的重要象征。兵马俑坑内出土了数千个陶制的士兵和马俑，每个陶俑都有独特的面部表情和姿态，展示了秦朝的军事力量和工艺水平。兵马俑博物馆是游客了解秦朝历史和文化的重要场所，每年吸引着大量国内外游客。

#### 西湖

西湖，位于浙江省杭州市，是中国最著名的湖泊之一，被誉为“人间天堂”。西湖以其秀美的自然风光和丰富的文化底蕴而闻名。湖面上点缀着三潭印月、雷峰塔、断桥等著名景点，湖畔的苏堤、白堤等园林更是美不胜收。春季的西湖，桃花盛开，春色满园；夏季的西湖，荷花绽放，清凉宜人；秋季的西湖，红叶满山，秋意盎然；冬季的西湖，雪景如画，别有一番风味。

#### 桂林山水

桂林山水，位于广西壮族自治区，以其壮丽的山水风光和独特的喀斯特地貌而著称。漓江是桂林山水的代表，游客可以乘坐竹筏或游船游览漓江，欣赏两岸的奇峰异石和清澈的江水。桂林的象山、七星公园、芦笛岩等景点也吸引了大量游客。桂林山水不仅美在自然，还蕴含着丰富的文化内涵，是游客体验中国山水文化的绝佳之地。

#### 九寨沟

九寨沟，位于四川省阿坝藏族羌族自治州，是中国最著名的自然景区之一。九寨沟以其多彩的湖泊、瀑布、雪山和森林而闻名，被誉为“童话世界”。景区内的珍珠滩、五花海、长海等景点美不胜收，吸引了无数游客前来观赏。九寨沟的四季各有特色，春季的桃花和杜鹃花，夏季的清凉绿意，秋季的红叶和金黄，冬季的雪景，都让人流连忘返。

#### 布达拉宫

布达拉宫，位于西藏自治区的首府拉萨，是西藏最著名的地标建筑。这座宏伟的宫殿建于公元7世纪，是藏传佛教的象征。布达拉宫依山而建，共有13层，高117米，是西藏历史和文化的象征。游客可以参观布达拉宫的各个殿堂，了解藏传佛教的历史和文化。布达拉宫不仅是宗教信仰的中心，也是游客了解西藏文化的重要窗口。

#### 长白山

长白山，位于吉林省东南部，是中国东北的著名山脉。长白山以其壮丽的自然风光和丰富的生物多样性而著称。长白山天池是世界上最深的高山湖泊之一，湖面海拔达2189米，湖水清澈碧蓝。此外，长白山的瀑布、温泉和原始森林等自然景观也吸引了大量游客。长白山还是中国著名的滑雪胜地，冬季的滑雪活动吸引了众多滑雪爱好者。

#### 西湖

西湖，位于浙江省杭州市，是中国最著名的湖泊之一，被誉为“人间天堂”。西湖以其秀美的自然风光和丰富的文化底蕴而闻名。湖面上点缀着三潭印月、雷峰塔、断桥等著名景点，湖畔的苏堤、白堤等园林更是美不胜收。春季的西湖，桃花盛开，春色满园；夏季的西湖，荷花绽放，清凉宜人；秋季的西湖，红叶满山，秋意盎然；冬季的西湖，雪景如画，别有一番风味。

#### 张家界

张家界，位于湖南省西北部，是中国著名的自然风景区。张家界以其独特的石柱地貌和壮丽的山水风光而闻名。景区内的袁家界、天子山、金鞭溪等景点美不胜收，吸引了无数游客前来观赏。张家界还是中国著名的电影拍摄地，如《阿凡达》等电影在此取景，使其名声大噪。张家界不仅自然风光优美，还拥有丰富的民俗文化和历史遗迹，是游客体验中国南方自然风光和文化的绝佳之地。

#### 颐和园

颐和园，位于北京市西郊，是中国古代皇家园林之一。颐和园建于清朝乾隆年间，占地面积达290公顷，是中国园林艺术的杰作。园内拥有万寿山、昆明湖、长廊、佛香阁等著名景点，建筑精美，景色宜人。颐和园不仅展示了中国的园林艺术，还蕴含了丰富的历史文化内涵，是游客了解中国古代皇家生活和文化的绝佳场所。

#### 西安城墙

西安城墙，位于陕西省西安市，是中国现存最完整的古代城墙之一。城墙建于明朝，全长约14公里，高约12米，厚约18米。游客可以登上城墙，俯瞰整个西安市区，感受古代都城的雄伟气势。城墙周边还有许多历史文化景点，如兵马俑、大雁塔等，是游客了解中国古代历史和文化的重要场所。

这些主要旅游景点不仅展示了中国的自然风光和历史文化，也为游客提供了丰富多彩的旅游体验。无论您是历史爱好者、自然探险家还是文化体验者，中国都有适合您的旅游目的地。

### 中国的美食文化

中国美食文化博大精深，各地特色美食琳琅满目，每一种都蕴含着独特的地域风情和文化内涵。从北方的面食到南方的米饭，从东部的海鲜到西部的牛羊肉，中国美食的多样性和丰富性令人叹为观止。

#### 北方美食

北方以面食为主，尤其是小麦面食，如北京炸酱面、山西刀削面、陕西油泼面等。北京炸酱面以其独特的酱料和面条口感闻名，是北京的传统美食代表。山西刀削面则以其独特的制作工艺和厚实的面条深受喜爱。陕西油泼面则是以热油浇在面上，香气扑鼻，味道鲜美。

此外，北方还有许多著名的肉类美食，如内蒙古的烤全羊、新疆的烤羊肉串和兰州的牛肉面。内蒙古的烤全羊以其肉质鲜嫩、香气四溢而著称，是蒙古族招待贵宾的最高礼遇。新疆的烤羊肉串则是街头巷尾常见的小吃，香气扑鼻，肉质鲜美，是新疆美食的代表。兰州的牛肉面以其独特的汤料和面条口感闻名，是兰州人的日常美食。

#### 南方美食

南方则以米饭和海鲜为主，如广东的早茶、四川的火锅、江苏的苏帮菜等。广东的早茶文化源远流长，以点心和茶饮为主，如虾饺、烧卖、蛋挞等，是广东人早晨必不可少的饮食。四川火锅以其麻辣鲜香而著称，是四川人喜爱的美食代表，无论是麻辣火锅还是清汤火锅，都能满足不同口味的需求。

江苏的苏帮菜则以清淡鲜美、注重原汁原味而闻名，如扬州炒饭、松鼠桂鱼等。苏帮菜讲究色、香、味、形的和谐统一，是江南美食的代表。此外，南方的海鲜美食也极具特色，如广东的清蒸海鲜、福建的佛跳墙、浙江的西湖醋鱼等。这些海鲜美食以其鲜美的口感和独特的烹饪方法吸引了无数游客。

#### 西部美食

西部地区的美食则以牛羊肉和面食为主，如新疆的抓饭、青海的羊肉泡馍、甘肃的拉面等。新疆的抓饭以其独特的烹饪方法和丰富的食材而著称，是新疆人喜爱的传统美食。青海的羊肉泡馍则是以羊肉汤和馍为主，口感鲜美，是青海的特色美食。甘肃的拉面以其独特的制作工艺和口感闻名，是甘肃人的日常美食。

#### 特色小吃

中国的小吃文化丰富多彩，各地的小吃都有其独特的风味和制作方法。如北京的豆汁、天津的狗不理包子、上海的生煎包、西安的肉夹馍、成都的麻辣串等。这些小吃不仅味道独特，还蕴含着丰富的文化内涵，是游客体验当地生活的重要途径。

总之，中国美食文化丰富多彩，各地的特色美食各具特色，无论是主食还是小吃，都能满足不同游客的口味需求。品尝中国美食，是了解中国文化和生活方式的重要方式之一。

### 中国的传统文化和节庆活动

中国是一个拥有悠久历史和丰富文化的国家，其传统文化和节庆活动丰富多彩，反映了中华民族的智慧和情感。以下是一些重要的中国传统文化和节庆活动：

#### 春节

春节，又称农历新年，是中国最重要的传统节日，通常在农历正月初一庆祝。春节象征着新的一年的开始，人们通过贴春联、放鞭炮、拜年、吃团圆饭等方式来庆祝。春节期间，家家户户都会打扫卫生，贴上红春联和窗花，营造喜庆的氛围。除夕夜，全家人会团聚在一起吃年夜饭，象征团圆和幸福。春节期间，还有舞龙舞狮、庙会等活动，吸引了大量游客前来体验中国的新年文化。

#### 清明节

清明节，通常在每年的4月4日或5日，是中国传统节日之一，也是祭祖扫墓的日子。清明节期间，人们会前往墓地祭拜祖先，扫墓、献花，表达对先人的敬意和怀念。此外，清明节还有踏青、赏花等活动，人们会到郊外散步，欣赏春天的美景。清明节不仅是一个重要的传统节日，也是人们亲近自然、放松心情的好时机。

#### 端午节

端午节，通常在农历五月初五庆祝，是中国传统节日之一。端午节有吃粽子、赛龙舟等传统习俗。粽子是端午节的传统食品，以糯米和各种馅料制成，形状多样，口味丰富。赛龙舟则是端午节最具代表性的活动，人们会组织龙舟比赛，以纪念古代爱国诗人屈原。端午节不仅是一个庆祝节日，也是传承和弘扬中华民族传统文化的重要时刻。

#### 中秋节

中秋节，通常在农历八月十五庆祝，是中国传统的团圆节日。中秋节以赏月、吃月饼为主要活动。月饼是中秋节的传统食品，形状圆饼，寓意团圆和圆满。人们会在晚上一起赏月，品尝月饼，表达对家人和亲友的思念和祝福。中秋节不仅是一个家庭团聚的日子，也是人们表达情感和思念的重要时刻。

#### 重阳节

重阳节，通常在农历九月初九庆祝，是中国传统节日之一。重阳节有登高、赏菊、吃重阳糕等传统习俗。登高是重阳节的重要活动，人们会到高处远眺，祈求健康和长寿。赏菊则是重阳节的一项重要活动，人们会欣赏各种美丽的菊花，感受秋天的气息。重阳节不仅是一个庆祝节日，也是人们祈求健康和长寿的重要时刻。

#### 其他传统节日

除了上述重要的传统节日外，中国还有许多其他传统节日，如元宵节、清明节、端午节、中秋节等。这些节日都有其独特的庆祝方式和传统习俗，反映了中华民族的智慧和情感。例如，元宵节有赏花灯、猜灯谜的习俗；清明节有踏青、扫墓的习俗；端午节有赛龙舟、吃粽子的习俗；中秋节有赏月、吃月饼的习俗。

总之，中国的传统文化和节庆活动丰富多彩，每一个节日都蕴含着深厚的文化内涵和民族情感。通过参与这些节日活动，游客不仅能感受到中国文化的魅力，还能更好地了解和体验中国的传统生活方式。

### 中国的购物体验

中国是一个购物天堂，无论是传统的手工艺品还是现代化的购物中心，都能满足游客的购物需求。以下是一些著名的购物地点和特色商品，供游客参考：

#### 北京

北京作为中国的首都，拥有丰富的购物资源。王府井大街是北京最著名的购物街之一，这里有各种国内外品牌和传统手工艺品店。此外，北京还有许多特色市场，如潘家园古玩市场，这里可以找到各种古董、艺术品和手工艺品。

特色商品：北京烤鸭、丝绸、景泰蓝、瓷器、古董。

#### 上海

上海是中国的经济中心，拥有众多高端购物中心和时尚品牌店。南京路步行街是上海最繁华的商业街之一，汇集了各种国内外品牌。此外，上海还有豫园商城，这里可以找到许多传统手工艺品和特色商品。

特色商品：丝绸、上海旗袍、珠宝、手表、茶叶。

#### 成都

成都是一个充满生活气息的城市，拥有许多特色市场和购物中心。宽窄巷子是成都的一个著名景点，也是购物的好去处。这里可以找到许多传统手工艺品和特色小吃。此外，成都还有春熙路、太古里等现代化购物中心。

特色商品：火锅底料、麻辣串、蜀锦、蜀绣、茶叶。

#### 西安

西安作为古都，拥有丰富的历史文化遗产和传统手工艺品。回民街是西安的一个著名景点，也是购物的好去处。这里可以找到各种传统小吃和手工艺品，如剪纸、陶器、皮影等。

特色商品：兵马俑复制品、剪纸、陶器、皮影、羊肉泡馍调料。

#### 桂林

桂林以其美丽的自然风光和丰富的民俗文化而闻名。在桂林的市区，游客可以找到许多特色商店和手工艺品店，如东西巷、正阳步行街等。这里可以购买到各种桂林特色商品，如桂林米粉、漓江石画、竹编等。

特色商品：桂林米粉、漓江石画、竹编、茶叶。

#### 香港

香港是国际化的购物天堂，拥有世界各地的品牌和特色商品。香港的购物中心如铜锣湾、尖沙咀等地，是购物的好去处。此外，香港还有许多著名的购物街，如苏豪区、中环等。

特色商品：珠宝、手表、化妆品、丝绸、电子产品。

#### 澳门

澳门以其独特的葡萄牙文化和丰富的美食而闻名。在澳门的购物区，如新葡京购物中心、威尼斯人购物中心等，游客可以找到各种国际品牌和特色商品。

特色商品：珠宝、手表、化妆品、葡式糕点、葡萄酒。

总之，中国的购物体验丰富多彩，无论是传统手工艺品还是现代化购物中心，都能满足游客的购物需求。游客可以根据自己的兴趣和需求，选择适合自己的购物地点和特色商品。

### 中国的住宿选择

中国拥有丰富的住宿选择，从豪华酒店到经济型旅馆，从传统客栈到青年旅舍，无论您的预算和喜好如何，都能找到合适的住宿地点。以下是一些常见的住宿类型和推荐：

#### 豪华酒店

豪华酒店通常位于城市中心或旅游景点附近，提供高品质的服务和设施。这些酒店通常拥有宽敞的客房、豪华的浴室、高级餐饮服务和健身中心等。例如，北京的中国大饭店、上海的浦东香格里拉大酒店、成都的成都希尔顿酒店等，都是豪华酒店的代表。豪华酒店适合追求舒适和品质的游客，尤其是商务旅行者和高端旅游者。

#### 经济型旅馆

经济型旅馆价格适中，提供基本的住宿设施，如干净整洁的客房、热水和空调等。这些旅馆通常位于城市的繁华地段或旅游景点附近，方便游客出行。例如，北京的如家快捷酒店、上海的7天连锁酒店、成都的汉庭酒店等，都是经济型旅馆的典型代表。经济型旅馆适合预算有限的游客，尤其是背包客和短期旅行者。

#### 传统客栈

传统客栈是中国特色的一种住宿方式，通常位于古城或古镇中，建筑风格古朴，内部装饰简约而典雅。这些客栈不仅提供住宿，还常常提供当地特色餐饮和旅游咨询服务。例如，丽江的四方街客栈、苏州的平江客栈、西安的回民街客栈等，都是传统客栈的典型代表。传统客栈适合喜欢体验当地文化和风情的游客。

#### 青年旅舍

青年旅舍是一种经济实惠的住宿选择，通常提供多人间和私人房间，适合年轻人和背包客。这些旅舍设施简单，但通常设有公共厨房、客厅和活动室等，方便游客交流和互动。例如，北京的青年旅舍、上海的青年旅舍、厦门的鼓浪屿青年旅舍等，都是青年旅舍的代表。青年旅舍适合喜欢结交新朋友和体验当地文化的年轻人。

#### 推荐住宿

1. **北京**：中国大饭店、如家快捷酒店、南锣鼓巷传统客栈。
2. **上海**：浦东香格里拉大酒店、7天连锁酒店、豫园传统客栈。
3. **成都**：成都希尔顿酒店、汉庭酒店、宽窄巷子传统客栈。
4. **丽江**：四方街客栈、丽江古城青年旅舍。
5. **苏州**：平江客栈、苏州园林酒店。
6. **厦门**：鼓浪屿青年旅舍、厦门国际酒店。

总之，中国的住宿选择丰富多样，无论您的预算和喜好如何，都能找到合适的住宿地点。选择适合自己的住宿，能让您的旅行更加舒适和愉快。

### 中国的旅游交通

中国的交通网络发达，为游客提供了便捷的出行方式。无论是国内航班、火车还是长途汽车，都能满足不同游客的出行需求。以下是一些主要的交通方式及其特点：

#### 国内航班

国内航班是中国游客长途旅行的主要交通方式之一。中国拥有众多大型机场，如北京首都国际机场、上海浦东国际机场、广州白云国际机场等，连接了国内外各大城市。国内航班通常快捷方便，适合远距离旅行。游客可以通过各大航空公司官网或在线旅行社预订机票，通常提前预订可以获得更优惠的价格。需要注意的是，国内航班通常需要提前办理登机手续和行李托运，建议游客提前到达机场，以免耽误行程。

#### 火车

中国的铁路网络非常发达，覆盖了全国大部分地区。中国的高速铁路（简称“高铁”）系统尤为先进，运行速度快，舒适度高，是长途旅行的重要选择。高铁线路连接了北京、上海、广州、成都、重庆等主要城市，运行时间通常在几小时以内。此外，普通火车线路也覆盖了偏远地区，适合预算有限的游客。火车票可以通过12306官网或火车站售票窗口购买。需要注意的是，节假日和旅游旺季期间，火车票可能较为紧张，建议游客提前预订。

#### 长途汽车

长途汽车是连接中小城市和偏远地区的主要交通方式。中国的长途汽车站通常位于城市中心或郊区，提供前往周边城市和景区的线路。长途汽车价格相对较低，适合预算有限的游客。游客可以通过车站售票窗口或在线旅行社预订车票。需要注意的是，长途汽车运行时间较长，乘坐体验相对较差，适合短途或预算有限的游客。

#### 城市交通

在城市内部，游客可以乘坐地铁、公交车、出租车和共享单车等交通工具。地铁是城市交通的主要方式，覆盖了大部分城市中心区域，运行速度快，票价合理。公交车则适合短途出行，价格便宜，但运行时间较长。出租车和网约车（如滴滴出行）则提供了便捷的出行选择，适合急需出行的游客。共享单车则方便游客在市区内短途骑行，适合喜欢户外活动的游客。

总之，中国的交通网络发达，为游客提供了多样化的出行选择。无论您选择哪种交通方式，都能方便快捷地到达目的地。提前规划行程和预订交通票务，能让您的旅行更加顺利和愉快。

### 中国的旅游安全和注意事项

在享受中国丰富多样的旅游体验时，游客需要关注一些旅游安全和注意事项，以确保旅行的顺利进行。以下是一些常见的旅游安全和健康问题，以及应对措施：

#### 安全问题

1. **随身物品安全**：在公共场所，如火车站、机场、旅游景点等，游客应时刻注意随身物品的安全。贵重物品应随身携带，避免放在无人看管的地方。此外，游客应避免夜间单独行动，尤其是在偏僻或人烟稀少的地方。

2. **交通安全**：在乘坐公共交通工具时，游客应遵守交通规则，如过马路时要走斑马线，乘坐出租车时要确保司机使用计价器。自驾游的游客应熟悉当地交通规则，遵守交通信号，确保行车安全。

3. **自然灾害**：中国部分地区可能发生自然灾害，如地震、洪水、台风等。游客在旅行前应关注目的地的天气和自然灾害预警，提前做好应对准备。在自然灾害发生时，游客应听从当地政府和导游的安排，避免前往危险区域。

4. **社会治安**：中国整体社会治安良好，但在一些地区，游客仍需注意个人安全。避免夜间单独外出，特别是在人烟稀少的地方。如遇到紧急情况，应及时报警并寻求帮助。

#### 健康问题

1. **饮食卫生**：中国的饮食文化丰富多样，但游客在品尝当地美食时，应特别注意饮食卫生。避免食用生冷食品、街边小吃和不熟悉的食物，以防食物中毒。游客还应携带一些常用的药物，如感冒药、消炎药、创可贴等。

2. **水土不服**：中国地域辽阔，各地水质和气候条件不同，游客在旅行过程中可能会出现水土不服的情况。建议游客提前准备一些常用的药物，如止泻药、消炎药等。此外，游客应多喝水，保持身体水分平衡。

3. **防晒和防蚊虫**：在户外活动时，游客应做好防晒措施，如涂抹防晒霜、戴帽子和太阳镜等。同时，应避免蚊虫叮咬，携带防蚊虫叮咬的药物和用品，如蚊香、防蚊液等。

4. **医疗保健**：游客在旅行前应了解目的地的医疗资源和保健设施，如医院、药店等。在旅行过程中，如出现身体不适，应及时就医。此外，游客应购买旅游保险，以应对可能的医疗费用和紧急情况。

总之，了解和关注旅游安全和健康问题，是确保旅行顺利进行的重要保障。游客在旅行前应做好充分的准备，遵守当地的规定和习俗，确保旅行的安全和愉快。

### 中国旅游的最佳季节

中国的气候多样，不同地区和季节各有特色，因此选择合适的旅游季节对提升旅行体验至关重要。以下是中国各地旅游的最佳季节及推荐理由：

#### 北方地区

**最佳旅游季节**：春季（3月至5月）和秋季（9月至11月）

**推荐理由**：
- **春季**：北方地区春季气温适中，万物复苏，绿意盎然。北京、天津等地的樱花盛开，哈尔滨的冰雪节也是春季的好时节，可以欣赏到美丽的冰雕和雪景。
- **秋季**：北方地区秋季气候宜人，秋高气爽，景色宜人。北京、西安等地的红叶季节，景色壮观，是摄影爱好者的最佳选择。此外，秋季的丰收季节，游客还可以品尝到各种新鲜的水果和美食。

#### 中部地区

**最佳旅游季节**：春季（3月至5月）和秋季（9月至11月）

**推荐理由**：
- **春季**：中部地区春季气温适中，气候宜人，是游览武汉、长沙等城市的最佳时节。此时，武汉的樱花盛开，长沙的岳麓山也是春游的好去处。
- **秋季**：中部地区秋季气候凉爽，秋高气爽，是游览南京、杭州等城市的理想季节。南京的桂花香气四溢，杭州的西湖美景更是令人陶醉。

#### 南方地区

**最佳旅游季节**：春季（3月至5月）和秋季（9月至11月）

**推荐理由**：
- **春季**：南方地区春季气候温暖，万物复苏，是游览广州、深圳等城市的最佳时节。此时，广州的荔枝花盛开，深圳的华侨城也是春季游玩的好地方。
- **秋季**：南方地区秋季气候宜人，秋高气爽，是游览厦门、福州等城市的理想季节。厦门的鼓浪屿、福州的三坊七巷等景点，秋季景色尤为迷人。

#### 西部地区

**最佳旅游季节**：夏季（6月至8月）和秋季（9月至11月）

**推荐理由**：
- **夏季**：西部地区夏季气候凉爽，是游览青藏高原、九寨沟等景区的最佳时节。青藏高原的蓝天白云、九寨沟的翠湖碧水，都是夏季的独特美景。
- **秋季**：西部地区秋季气候宜人，秋高气爽，是游览新疆、甘肃等地的理想季节。此时，新疆的瓜果飘香，甘肃的丹霞地貌色彩斑斓，景色壮观。

总之，选择合适的旅游季节，不仅能享受到最佳的自然风光，还能避免旅游高峰期的人流拥挤，提升旅行的舒适度和体验感。游客可以根据自己的兴趣和需求，选择适合的季节前往中国各地旅游。

### 中国旅游的实用小贴士

为了确保您的中国之旅顺利愉快，以下是一些实用的旅游小贴士，帮助您更好地准备和应对旅行中的各种情况：

#### 旅行前的准备

1. **签证办理**：根据您的国籍和旅行目的，提前办理相应的签证。中国签证办理流程较为复杂，建议提前了解并准备好所有必要的材料。

2. **行程规划**：提前规划您的旅行路线和行程，包括景点、住宿、交通等。这样可以避免在旅途中因不确定因素而浪费时间。

3. **预订机票和酒店**：提前预订机票和酒店，可以享受更优惠的价格。特别是在旅游旺季，提前预订可以确保您的行程顺利。

4. **购买旅游保险**：购买旅游保险，以应对可能的突发情况，如意外伤害、疾病、行李丢失等。

5. **了解当地文化和习俗**：在旅行前，了解目的地的文化和习俗，尊重当地的风俗习惯，避免不必要的冲突。

#### 旅行中的注意事项

1. **随身携带重要文件**：如护照、签证、身份证、机票等，并确保这些文件的安全。

2. **随身物品**：携带一些必要的随身物品，如钱包、手机、相机、充电器、转换插头等。同时，注意保管好贵重物品，避免丢失或被盗。

3. **交通规则**：熟悉目的地的交通规则，特别是在自驾游时，遵守交通信号和规定，确保行车安全。

4. **饮食卫生**：在品尝当地美食时，注意饮食卫生，避免食用生冷食品和不熟悉的食物，以防食物中毒。

5. **防晒和防蚊虫**：在户外活动时，做好防晒和防蚊虫叮咬的措施，携带防晒霜、防蚊液等用品。

#### 应对突发情况

1. **紧急情况**：如遇紧急情况，如丢失证件、生病、意外伤害等，及时报警并联系旅行社或当地朋友寻求帮助。

2. **医疗保健**：了解目的地的医疗资源和保健设施，如医院、药店等。在旅行前准备一些常用的药物，如感冒药、消炎药、创可贴等。

3. **网络通讯**：确保手机和网络畅通，可以购买当地的电话卡或使用国际漫游服务，以便在紧急情况下与家人和朋友联系。

总之，通过充分的准备和注意旅行中的细节，您可以确保中国之旅顺利愉快。这些实用小贴士将帮助您更好地应对旅行中的各种情况，享受美好的旅程。

### 中国旅游的总结与展望

中国，这片古老而神秘的东方土地，以其丰富的历史、多样的自然风光和独特的文化，吸引了无数游客。从长城的巍峨壮观到故宫的宏伟壮丽，从九寨沟的碧水蓝天到丽江古城的宁静古朴，每一个景点都让人流连忘返。中国的美食文化更是让人垂涎欲滴，无论是北方的面食、南方的米饭，还是西部地区的牛羊肉，每一种美食都蕴含着深厚的文化底蕴。此外，中国的传统文化和节庆活动丰富多彩，从春节的团圆到端午节的龙舟竞渡，每一个节日都让人感受到浓厚的民族情感。

中国旅游的魅力不仅在于其丰富的自然和人文景观，更在于其热情好客的人民。无论您是历史爱好者、自然探险家还是文化体验者，都能在中国找到属于自己的旅游天堂。无论是繁华的都市、宁静的古镇，还是壮丽的自然景观，中国都能满足您的旅游需求。

展望未来，中国将继续加大对旅游基础设施的投入，提升旅游服务质量，为全球游客提供更加便捷和舒适的旅游体验。随着中国旅游业的不断发展，更多的国际游客将来到中国，探索这片古老而神秘的东方土地。

我们诚挚地邀请您来中国旅游，感受这片土地的独特魅力。无论是历史遗迹、自然风光还是美食文化，中国都将为您带来难忘的旅行体验。期待您的到来，一起探索中国的美丽与神奇！

</div>
</details>

<a name="citation"></a>
## 📝 Citation

If you find our work useful, please kindly cite:

```
@article{bai2024longwriter,
  title={LongWriter: Unleashing 10,000+ Word Generation from Long Context LLMs}, 
  author={Yushi Bai and Jiajie Zhang and Xin Lv and Linzhi Zheng and Siqi Zhu and Lei Hou and Yuxiao Dong and Jie Tang and Juanzi Li},
  journal={arXiv preprint arXiv:2408.07055},
  year={2024}
}
```

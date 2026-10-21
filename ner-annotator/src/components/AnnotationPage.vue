<template>
  <div>
    <classes-block />

    <div class="page" style="display: flex;flex-direction: column; gap: 16px;">

      <div class="q-pa-lg" style="height:40vh; overflow-y:scroll;">
        <component
          :is="t.type === 'token' ? 'Token' : 'TokenBlock'"
          v-for="t in tm.tokens"
          :id="'t' + t.start"
          :key="t.start"
          :token="t"
          :background-color="t.backgroundColor"
          @remove-block="onRemoveBlock"
        />
      </div>
      <div class="page" style="overflow-y: scroll; height: 12vh; background-color: #f9fafb; border: 1px solid #d1d5db; border-radius: 5px; padding: 10px; width: 98%; align-self: center;">
          <Text style="font-size: 1.1rem; font-weight: bold; color: #374151;  margin-top: 40px; "> Explanations: </Text> <br/>
    <div id="content"></div>
      </div>

      <div style="display: flex; flex-direction: row; margin-top: -1%; ">
      <div class="page" style="overflow-y: scroll; height: 14vh; background-color: #f9fafb; border: 1px solid #d1d5db; border-radius: 5px; padding: 15px; width: 48%; margin: 1%;">
      <Text style="font-size: 1.1rem; font-weight: 600; color: #374151;  margin-top: 40px;"> Added Spans: </Text>
        <component
          :is="( t.type === 'token-block' )? 'TokenBlock' : ''"
          v-for="t in getFilteredTokens()"
          :id="'t' + t.start"
          :key="t.start"
          :token="t"
          :background-color="t.backgroundColor"
          style="  margin: 5px; background-color: #e5e7eb; "
          @remove-block="onRemoveBlock"
        />
      </div>

        <div class="page" style="overflow-y: scroll; height: 14vh; background-color: #f9fafb; border: 1px solid #d1d5db; border-radius: 5px; padding: 15px; width: 48%;margin: 1%; ">
      <Text style="font-size: 1.1rem; font-weight: 600; color: #374151;  margin-top: 40px;"> Removed Spans: </Text>
        <component
          :is="( t.type === 'token-block' )? 'TokenBlock' : ''"
          v-for="t in getDeselectedTokens()"
          :id="'t' + t.start"
          :key="t.start"
          :token="t"
          :background-color="t.backgroundColor"
          style="  margin: 5px; background-color: #e5e7eb; "
          @remove-block="resetBlocks"
          />
      </div>
      </div>

    <div>
  </div>

    </div>

    <div class="q-pa-md">
      <q-btn color="red" outline class="q-mx-sm" label="Reset" @click="resetBlocks" />
      <q-btn class="q-mx-sm" color="green-7" outline 
      :label = "isSaving ? '\u2713':'Save'"
      @click="SaveAndGetConfig" />
    </div>
  </div>
</template>

<script>
import { mapState, mapMutations } from "vuex";
import Token from "./Token";
import TokenBlock from "./TokenBlock";
import ClassesBlock from "./ClassesBlock.vue";
import TokenManager from "./token-manager";
import TreebankTokenizer from "treebank-tokenizer";
import eventBus from './eventBus';
import { API_BASE_URL } from "../config/api";

export default {
  name: "AnnotationPage",
  components: {
    Token,
    TokenBlock,
    ClassesBlock,
  },
  
  emits: ["review-spans"],

  data: function() {
    return {
      tm: new TokenManager([]),
      currentSentence: {},
      redone: "",
      tokenizer: new TreebankTokenizer(),
      tokens_initial: [],
      isSaving:false,
      config:[],
      selectedCountry: '',
      selectedAgeGroup: '',
      selectedRegion: '',
      text: '',
      Initial_Response: [],
      PoliticalAwareness: '',
      LiteraturePreference: '',
      EducationLevel: '',
      FoodCuisine: '',
      Explanations: '',

    };
  },
  computed: {
    ...mapState([
      "annotations",
      "classes",
      "currentClass",
      "currentIndex",
      "inputSentences",
      "annotationPrecision",
    ]),
  },
  watch: {
    inputSentences() {
      this.resetIndex();
      this.tokenizeCurrentSentence();
    },
    annotations() {
      if (this.currentAnnotation != this.annotations[this.currentIndex]) {
        this.tokenizeCurrentSentence();
      }
    },
    classes() {
      this.tokenizeCurrentSentence();
    },
    annotationPrecision() {
      this.tokenizeCurrentSentence();
    }
  },
  created() {
    if (this.inputSentences.length) {
      this.tokenizeCurrentSentence();
      
    }
    document.addEventListener("mouseup", this.selectTokens);
    document.addEventListener('keydown', this.keypress);
  },
  mounted(){
    this.tokens_initial = this.tm.tokens
    eventBus.value.tokens_initial = this.tm.tokens;
    this.config = eventBus.value.config || [];
    this.selectedCountry= eventBus.value.selectedCountry || '';
    this.selectedAgeGroup= eventBus.value.selectedAgeGroup || '';
    this.selectedRegion= eventBus.value.selectedRegion || '';
    this.text = eventBus.value.text || '';
    this.Initial_Response= eventBus.value.Initial_Response || [];
    this.PoliticalAwareness = eventBus.value.PoliticalAwareness || '';
    this.LiteraturePreference = eventBus.value.LiteraturePreference || '';
    this.EducationLevel = eventBus.value.EducationLevel || '';
    this.FoodCuisine = eventBus.value.FoodCuisine || '';
    
    this.FitExplanationsInsideContent();


  },

  beforeUnmount() {
    document.removeEventListener("mouseup", this.selectTokens);
    document.removeEventListener("keydown", this.keypress);
  },
  methods: {
    ...mapMutations(["nextSentence", "previousSentence", "resetIndex"]),

    FitExplanationsInsideContent(){

      const contentDiv = document.getElementById('content');
      this.Explanations = eventBus.value.Explanations;

      for(let i = 0; i < this.Explanations.length; i++) {

        let p = document.createElement('p');
        let item = `<strong>${i+1}. ${this.Explanations[i].CSI}</strong> - ${this.Explanations[i].explanation}`;
        p.innerHTML = item; 

  // p.textContent = item;
  p.style.margin = '5px 0';
  p.style.fontFamily = 'Arial, sans-serif';
  p.style.fontSize = '1.1rem';
  p.style.color = '#333'; // Dark gray text for readability

  contentDiv.appendChild(p);

}

    },


    tokenizeCurrentSentence() { 
      this.currentSentence = this.inputSentences[this.currentIndex];
      this.currentAnnotation = this.annotations[this.currentIndex];

      let tokens, spans;

      tokens = this.tokenizer.tokenize(this.currentSentence.text);
      spans = this.tokenizer.span_tokenize(this.currentSentence.text);

      let combined = tokens.map((t, i) => [spans[i][0], spans[i][1], t]);
      this.tm = new TokenManager(this.classes);
      this.tm.setTokensAndAnnotation(combined, this.currentAnnotation);
    },

    getFilteredTokens() {
      return this.tm.tokens.filter(t => !this.tokens_initial.includes(t));
    },

    getDeselectedTokens() {
      return this.tokens_initial.filter(t => !this.tm.tokens.includes(t));
    },

    selectTokens() { 
      let selection = document.getSelection();

      if (
        selection.anchorOffset === selection.focusOffset &&
        selection.anchorNode === selection.focusNode
      ) {
        return;
      }
      
      const rangeStart = selection.getRangeAt(0);
      const rangeEnd = selection.getRangeAt(selection.rangeCount - 1);
      let start, end;
      try {
        start = parseInt(rangeStart.startContainer.parentElement.id.replace("t", ""));
        let offsetEnd = parseInt(rangeEnd.endContainer.parentElement.id.replace("t", ""));
        end = offsetEnd + rangeEnd.endOffset;
        if(!end){
          /* 
            If last node of selected text contains tag name 
            Fetch the previous node
          */
          const endContainerParent = rangeEnd.endContainer.parentNode;
          const previousNode = endContainerParent.previousSibling;
          offsetEnd = parseInt(previousNode.parentElement.id.replace("t",""))
          end = offsetEnd + rangeEnd.endOffset;
        }
      } catch {
        return;
      }
      
      this.tm.addNewBlock(start, end, this.currentClass);
      selection.empty();
    },
    onRemoveBlock(blockStart) {
      this.tm.removeBlock(blockStart);
    },

    onAddBlock(start,end,currentClass){
      this.tm.addNewBlock(start,end,currentClass);
    },

    resetBlocks() {
      // console.log(this.tm.TokenBlock)
      this.tm.resetBlocks();
    },
    skipCurrentSentence() {
      this.nextSentence();
      this.tokenizeCurrentSentence();
    },
    backOneSentence() {
      this.previousSentence();
      this.tokenizeCurrentSentence();
    },
    SaveAndGetConfig(){
      eventBus.value.tokens_final = this.tm.tokens;
      this.isSaving = true;
      setTimeout(() =>{
        this.$emit("review-spans");
        this.isSaving = false;
      },400)

      const token_block_body = this.tm.tokens.filter(token => token.type === 'token-block');
      const token_block_initial = this.tokens_initial.filter(token => token.type === 'token-block');

      

      fetch(`${API_BASE_URL}/gateway`, {
        method: 'POST', 
        headers: {
          'Content-Type': 'application/json',  
        },
        body: JSON.stringify({
          'type':'save_info',
          'country':this.selectedCountry,
          'region':this.selectedRegion,
          'age_group':this.selectedAgeGroup,
          "annotations_response":this.Initial_Response,
          'annotations_updated':{'token_block_body':token_block_body,'token_block_initial':token_block_initial},
          'messages': this.config ? this.config : [],
          'url': this.text,
          'political_awareness': this.PoliticalAwareness ,
          'education_level': this.EducationLevel,
          'literature_preference': this.LiteraturePreference,
          'food_cuisine': this.FoodCuisine ,

        })  
      })
      .then(response => {
        if (!response.ok) {
          throw new Error('Network response was not ok');
        }
        return response.json(); 
      })
      .then(data => {
        this.config = data['messages'];
        eventBus.value.config = this.config; 
        console.log("updated Config:",this.config);
        eventBus.value.Explanations = data.explanations;
        
        eventBus.value.PoliticalAwareness = data["political_awareness"];
        eventBus.value.LiteraturePreference = data["literature_preference"];
        eventBus.value.EducationLevel = data["education_level"];
        eventBus.value.FoodCuisine = data["food_cuisine"];

        return;
      })
      .catch(error => {
        console.error('There was a problem with the fetch operation:', error);
        return;
      });
    },


    saveTags() {
      this.$store.commit("addAnnotation", {
        text: this.currentSentence.text,
        entities: this.tm.exportAsAnnotation(),
      });
      this.nextSentence();
      this.tokenizeCurrentSentence();
    },
  },
};
</script>

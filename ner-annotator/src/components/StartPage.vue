<template>
  <Loader v-if="isLoading" />
  <div v-else>
    <div class="q-mx-auto q-my-xl" style="max-width: 800px; margin-right: 25%;">
      <!-- <p v-if="config.length !== 0" style="margin-left: 35%;">[Your information is saved with us!]</p> -->
      <div style="display: flex; align-items: center; width: 100%;  margin-top: 35%; margin-bottom: 15%;">
        <input
          :placeholder="this.config.length !== 0 ? 'Try another URL!' : 'Enter the URL here!'"
          :value="text"
          @input="event => text = event.target.value"
          style="flex: 1; padding: 15px; border-radius: 10px 0 0 10px;background-color: #f7f7f7; border: 0px solid #f7f7f7; box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2); font-size: 18px; outline: none; "
        />
        <button
          @click="onConfirmation(text)"
          style="padding: 17.5px 40px; border-radius: 0 10px 10px 0; border: 0px solid #ccc; background-color: #4CAF50; color: white; cursor: pointer; box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2); font-size: 16px;"
        >
          &#8594;
        </button>
      </div>

      <div style="margin-left: 5%;">
<h5 style="font-size: 17px; font-weight: bold; color: #333; margin-bottom: 30px;">Let us know more about you:</h5>
        
        <!-- <label for="country">Country:</label> -->
        <select v-model="selectedCountry" id="country">
          <option disabled value="">Select your country</option>
          <option v-for="country in countries" :key="country" :value="country">{{ country }}</option>
        </select>

        <!-- <label for="age-group">Age Group:</label> -->
        <select v-model="selectedAgeGroup" id="age-group">
          <option disabled value="">Select your age group</option>
          <option v-for="ageGroup in ageGroups" :key="ageGroup" :value="ageGroup">{{ ageGroup }}</option>
        </select>

        <!-- <label for="region">Region:</label> -->
        <select v-model="selectedRegion" id="region">
          <option disabled value="">Select your region</option>
          <option v-for="region in regions" :key="region" :value="region">{{ region }}</option>
        </select>
      </div>

    </div>
  </div>
</template>


<script>
import { mapMutations } from "vuex";
import Loader from './Loader.vue';
import eventBus from './eventBus';
import { API_BASE_URL } from "../config/api";

export default {
  name: "StartPage",
  emits: ["file-loaded"],
  components: {
    Loader,
  },
  data() {
    return {
      text: '',
      annotationFile: null,
      isLoading: false,
      config: [],
      selectedCountry: '',
      selectedAgeGroup: '',
      selectedRegion: '',
      PoliticalAwareness: '',
      LiteraturePreference: '',
      EducationLevel: '',
      FoodCuisine: '',
      Explanations: '',
      
      countries: ['Afghanistan', 'Albania', 'Algeria', 'Andorra', 'Angola', 'Antigua and Barbuda', 'Argentina', 'Armenia', 'Australia', 'Austria', 'Azerbaijan', 'Bahamas', 'Bahrain', 'Bangladesh', 'Barbados', 'Belarus', 'Belgium', 'Belize', 'Benin', 'Bhutan', 'Bolivia', 'Bosnia and Herzegovina', 'Botswana', 'Brazil', 'Brunei', 'Bulgaria', 'Burkina Faso', 'Burundi', 'Cabo Verde', 'Cambodia', 'Cameroon', 'Canada', 'Central African Republic', 'Chad', 'Chile', 'China', 'Colombia', 'Comoros', 'Congo, Democratic Republic of the', 'Congo, Republic of the', 'Costa Rica', 'Croatia', 'Cuba', 'Cyprus', 'Czech Republic', 'Denmark', 'Djibouti', 'Dominica', 'Dominican Republic', 'East Timor', 'Ecuador', 'Egypt', 'El Salvador', 'Equatorial Guinea', 'Eritrea', 'Estonia', 'Eswatini', 'Ethiopia', 'Fiji', 'Finland', 'France', 'Gabon', 'Gambia', 'Georgia', 'Germany', 'Ghana', 'Greece', 'Grenada', 'Guatemala', 'Guinea', 'Guinea-Bissau', 'Guyana', 'Haiti', 'Honduras', 'Hungary', 'Iceland', 'India', 'Indonesia', 'Iran', 'Iraq', 'Ireland', 'Israel', 'Italy', 'Ivory Coast', 'Jamaica', 'Japan', 'Jordan', 'Kazakhstan', 'Kenya', 'Kiribati', 'Korea, North', 'Korea, South', 'Kuwait', 'Kyrgyzstan', 'Laos', 'Latvia', 'Lebanon', 'Lesotho', 'Liberia', 'Libya', 'Liechtenstein', 'Lithuania', 'Luxembourg', 'Madagascar', 'Malawi', 'Malaysia', 'Maldives', 'Mali', 'Malta', 'Marshall Islands', 'Mauritania', 'Mauritius', 'Mexico', 'Micronesia', 'Moldova', 'Monaco', 'Mongolia', 'Montenegro', 'Morocco', 'Mozambique', 'Myanmar', 'Namibia', 'Nauru', 'Nepal', 'Netherlands', 'New Zealand', 'Nicaragua', 'Niger', 'Nigeria', 'North Macedonia', 'Norway', 'Oman', 'Pakistan', 'Palau', 'Panama', 'Papua New Guinea', 'Paraguay', 'Peru', 'Philippines', 'Poland', 'Portugal', 'Qatar', 'Romania', 'Russia', 'Rwanda', 'Saint Kitts and Nevis', 'Saint Lucia', 'Saint Vincent and the Grenadines', 'Samoa', 'San Marino', 'Sao Tome and Principe', 'Saudi Arabia', 'Senegal', 'Serbia', 'Seychelles', 'Sierra Leone', 'Singapore', 'Slovakia', 'Slovenia', 'Solomon Islands', 'Somalia', 'South Africa', 'South Sudan', 'Spain', 'Sri Lanka', 'Sudan', 'Suriname', 'Sweden', 'Switzerland', 'Syria', 'Taiwan', 'Tajikistan', 'Tanzania', 'Thailand', 'Togo', 'Tonga', 'Trinidad and Tobago', 'Tunisia', 'Turkey', 'Turkmenistan', 'Tuvalu', 'UAE', 'Uganda', 'Ukraine', 'United Kingdom', 'Uruguay','USA','Uzbekistan', 'Vanuatu', 'Vatican City', 'Venezuela', 'Vietnam', 'Yemen', 'Zambia', 'Zimbabwe'],
      ageGroups: ['Adult (18+)', 'Teenager','Old (60+)'],
      regions: ['Rural', 'Urban'],
      Initial_Response: [],
    };
  },
  mounted() {
    this.config = eventBus.value.config || [];
    this.selectedCountry= eventBus.value.selectedCountry || '';
    this.selectedAgeGroup= eventBus.value.selectedAgeGroup || '';
    this.selectedRegion= eventBus.value.selectedRegion || '';
    this.PoliticalAwareness = eventBus.value.PoliticalAwareness || 'No',
    this.LiteraturePreference = eventBus.value.LiteraturePreference || 'English',
    this.EducationLevel = eventBus.value.EducationLevel || 'Primary',
    this.FoodCuisine = eventBus.value.FoodCuisine || 'American'
        
  },
  methods: {
    ...mapMutations(["setInputSentences", "loadAnnotations"]),
    
    isUrlValid(str) {
    const pattern = new RegExp(
      '^(https?:\\/\\/)?' +
        '((([a-z\\d]([a-z\\d-]*[a-z\\d])*)\\.)+[a-z]{2,}|' + 
        '((\\d{1,3}\\.){3}\\d{1,3}))' + 
        '(\\:\\d+)?(\\/[-a-z\\d%_.~+]*)*' + 
        '(\\?[;&a-z\\d%_.~+=-]*)?' +
        '(\\#[-a-z\\d_]*)?$', 
      'i'
    );
    return pattern.test(str);
    },

    onConfirmation(url) {
      
      if(this.selectedCountry === ''){
        this.selectedCountry = 'USA';
      }

      if(this.selectedAgeGroup === ''){
        this.selectedAgeGroup = 'Adult (18+)';
      }

      if(this.selectedRegion === ''){
        this.selectedRegion = 'Urban';
      }



      eventBus.value.text = this.text
      eventBus.value.selectedCountry = this.selectedCountry;
      eventBus.value.selectedAgeGroup = this.selectedAgeGroup;
      eventBus.value.selectedRegion = this.selectedRegion;
      
      if (!this.text.trim()) {
        alert('Please enter a value!');
        return;
      }


      
      let type_interaction = ''
      if(this.config.length === 0){
        type_interaction = 'fresh';
      }else{
        type_interaction = 'old';
      }

      this.isLoading = true;
      this.config = eventBus.value.config || [];

      if (url) {
        fetch(`${API_BASE_URL}/gateway`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            'type': type_interaction, 
            'url': url, 
            'messages': JSON.stringify(this.config), 
            'country':this.selectedCountry, 
            'age_group':this.selectedAgeGroup , 
            'region': this.selectedRegion,
            'political_awareness':this.PoliticalAwareness ,
            'education_level':this.EducationLevel,
            'literature_preference':this.LiteraturePreference,
            'food_cuisine':this.FoodCuisine,
            
          })
        })
          .then(response => {
            
            if (!response.ok) {
              throw new Error('Network response was not ok');
            }
            return response.json();
          })
          .then(data => {
            this.isLoading = false;
            this.$emit("file-loaded");
            this.setInputSentences(data['annotations_response']['annotations'][0][0]);
            this.loadAnnotations(data['annotations_response']);
            eventBus.value.Initial_Response = data['annotations_response'];
            eventBus.value.PoliticalAwareness = data["political_awareness"];
            eventBus.value.LiteraturePreference = data["literature_preference"];
            eventBus.value.EducationLevel = data["education_level"];
            eventBus.value.FoodCuisine = data["food_cuisine"];

            this.config = data['messages'];
            eventBus.value.config = this.config;

            eventBus.value.Explanations = data.explanations;

            
            // const p = document.createElement('p');
            // p.textContent = JSON.stringify(item);  // Adjust as per item structure
            // contentDiv.appendChild(p);


            return;
          })
          .catch(error => {
            console.error('There was a problem with the fetch operation:', error);
            this.isLoading = false;
            this.$emit("error-page");            
            return;
          });

        console.log("Got the response!");
        // setTimeout(() => {
        //   this.isLoading = false;
        //   this.$emit("file-loaded");
        // }, 3000);
      }
    },
  },
};
</script>

<style scoped>
select {
  margin-bottom: 15px;
  width: 25%;
  padding: 14px;
  font-size: 13px;
  margin-right: 5%;
  margin-left: 0;
  border-radius: 5px;
  border: 1px solid #ccc;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

h3 {
  margin-bottom: 10px;
}
</style>

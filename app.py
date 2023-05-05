from streamlit_player import st_player
import streamlit as st
import pickle
import pandas as pd
import requests
import gzip

st.set_page_config(layout="wide")

movies_dict=pickle.load(open('movies_dict.pkl','rb'))
# similarity=pickle.load(open('similarity.pkl','rb'))
movies = pd.DataFrame(movies_dict)

with gzip.open('similarity.pkl.gz', 'rb') as f:
    similarity = pickle.load(f)


def fetch_poster(movie_id):
    response=requests.get(f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=96aef6c0d373ea579771046d96e72e06")
    data=response.json()
    return "https://image.tmdb.org/t/p/w500/"+data['poster_path']

def fetch_youtube(movie_id):
    response=requests.get(f"http://api.themoviedb.org/3/movie/{movie_id}/videos?api_key=96aef6c0d373ea579771046d96e72e06")
    data=response.json()

    return "https://www.youtube.com/watch?v="+data["results"][0]["key"]

def fetch_detail(movie_id):
    response=requests.get(f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=96aef6c0d373ea579771046d96e72e06")
    data=response.json()
    
    detail={"Description":data['overview'],
            "Genres":[i['name'] for i in data['genres']],
            "Rating":data['vote_average']
           }
    return detail

def recommend(movie):
    movie_index=movies[movies['title']==movie].index[0] 
    distances=similarity[movie_index]
    movies_list=sorted(list(enumerate(distances)),reverse=True,key=lambda x:x[1])[1:6]
    
    recommended_movies=[]
    recommended_movies_poster=[]
    recommended_movies_trailer=[]
    recommended_movies_details=[]

    for i in movies_list:
        # fetch youtube video
        recommended_movies_trailer.append(fetch_youtube(movies.iloc[i[0]].id))
        
        # fetch poster using Api
        recommended_movies_poster.append(fetch_poster(movies.iloc[i[0]].id))
        
        # fetching moving title
        recommended_movies.append(movies.iloc[i[0]].title)

        # fetching other details
        recommended_movies_details.append(fetch_detail(movies.iloc[i[0]].id))

    return recommended_movies,recommended_movies_poster,recommended_movies_trailer,recommended_movies_details


st.title("Movie Recommender System")

movie=st.selectbox("Select a movie",movies['title'].values)


if st.button("Recommend"):
    st.subheader(f"Movies like {movie}")

    title,poster,trailer,detail=recommend(movie)

    for i in range(5):
        st.write("")
        tab1, tab2 = st.tabs(["Movie Datails","Trailer"])

        with tab1:
            col1,col2=st.columns(2)

            with col1:
                st.image(poster[i])
            with col2:
                st.subheader(title[i])            
                
                st.subheader(f"Summary-")
                st.write(detail[i]['Description'])

                st.markdown( f"Rating - :star2: {detail[i]['Rating']}")

                st.write(f"Genre - {', '.join(detail[i]['Genres'])}")

        with tab2:
            st.subheader(f"Trailer - {title[i]}") 
            st_player(trailer[i])

        st.write("")
        st.write("")
